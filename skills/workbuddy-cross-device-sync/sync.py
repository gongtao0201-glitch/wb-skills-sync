#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkBuddy 跨设备同步技能  (workbuddy-cross-device-sync)
把本机的"大脑"——用户级技能(~/.workbuddy/skills) + 用户级记忆(MEMORY.md)——
同步到另一台装了同技能的电脑,实现技能和记忆互通。

支持两种中转(在 init 时选择):
  - folder : 一个共享/同步盘目录(局域网 SMB 或 云盘同步空间),零外部依赖
  - git    : 一个 Git 仓库(推荐 GitHub 私有仓库, 跨网/跨地点通用)

git 模式说明:
  - 优先使用 GitHub Desktop 自带 git, 自动复用它的登录态(无需手动 PAT/SSH)
  - remote 填仓库 URL(如 https://github.com/<你>/wb-skills-sync.git)
  - 首次 init 若 GitHub 仓库不存在, 会用登录态 token 自动创建私有仓库
  - 首次运行会自动 clone 到技能目录下的 .repo 缓存, 之后 pull/push 都走它
  - 走本机 env 里的 HTTPS_PROXY/HTTP_PROXY 代理(适配国内上网环境)

安全策略:
  - 排除 settings.json / mcp.json(含 API key / OAuth 令牌, 绝不外传)
  - 排除 node_modules / __pycache__ / .git / _backup / *.log
  - 每次覆盖目标前自动备份到 _backup/<时间戳>, 可回滚
"""

import os
import json
import shutil
import datetime
import argparse
import subprocess
import re
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

APP = Path(os.environ.get("USERPROFILE", Path.home())) / ".workbuddy"
SKILL_DIR = Path(__file__).resolve().parent
CONFIG = SKILL_DIR / "config.json"
BACKUP = SKILL_DIR / "_backup"
GIT_REPO = APP / ".wb-sync" / "repo"   # git 模式本地缓存,放在 APP 下避免与技能目录互相嵌套
MANIFEST = APP / ".wb-sync" / "manifest.json"  # 本机上次推送的内容快照, 不随技能同步
MACHINE = os.environ.get("COMPUTERNAME", "unknown")

# 同步时永远忽略的东西
IGNORE = shutil.ignore_patterns(
    "node_modules", "__pycache__", ".git", "_backup", ".repo",
    "*.log", "settings.json", "mcp.json",
)


def find_desktop_git():
    """查找 GitHub Desktop 自带 git。它才能复用 Desktop 的登录态。"""
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "GitHubDesktop"
    if not base.exists():
        return None
    # 找最新版本目录
    apps = sorted([d for d in base.iterdir() if d.is_dir() and d.name.startswith("app-")], reverse=True)
    for app in apps:
        candidates = [
            app / "resources" / "app" / "git" / "cmd" / "git.exe",
            app / "resources" / "app" / "git" / "mingw64" / "bin" / "git.exe",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    return None


# 优先 GitHub Desktop 自带 git(复用登录态), 否则 fallback 系统 git
GIT_BIN = find_desktop_git() or shutil.which("git") or "git"


def log(*a):
    print("[wb-sync]", *a, flush=True)


def load_cfg():
    if CONFIG.exists():
        try:
            return json.loads(CONFIG.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cfg(cfg):
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def git_env():
    """git 子进程继承当前环境(含 HTTPS_PROXY 等代理), 以便国内网络可达 GitHub。"""
    return os.environ.copy()


def get_github_token():
    """通过 git credential fill 获取 GitHub token(依赖 Desktop 登录态)。"""
    try:
        r = subprocess.run(
            [GIT_BIN, "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, env=git_env(), timeout=15
        )
        if r.returncode != 0:
            return None
        for line in r.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def parse_github_remote(remote):
    """从 https://github.com/owner/repo.git 或 git@github.com:owner/repo.git 解析 owner/repo。"""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$", remote)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", remote)
    if m:
        return m.group(1), m.group(2)
    return None, None


def github_api(token, url, method="GET", data=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "workbuddy-cross-device-sync",
    }
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    else:
        body = None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")
    except Exception as e:
        return 0, {"error": str(e)}


def ensure_github_repo(remote):
    """若 remote 是 GitHub 且仓库不存在, 用 Desktop 登录态自动创建私有仓库。"""
    owner, repo = parse_github_remote(remote)
    if not owner or not repo:
        return
    token = get_github_token()
    if not token:
        log("提示: 未获取到 GitHub 登录态, 请确认 GitHub Desktop 已登录; 跳过自动创建仓库")
        return
    # 检查仓库是否存在
    status, body = github_api(token, f"https://api.github.com/repos/{owner}/{repo}")
    if status == 200:
        log(f"GitHub 仓库 {owner}/{repo} 已存在")
        return
    if status == 404:
        log(f"仓库 {owner}/{repo} 不存在, 正在用当前登录态自动创建私有仓库...")
        status2, body2 = github_api(
            token, "https://api.github.com/user/repos", "POST",
            {"name": repo, "private": True, "description": "WorkBuddy 跨设备技能与记忆同步"}
        )
        if status2 == 201:
            log(f"✅ 已创建私有仓库: {body2.get('html_url', remote)}")
        else:
            msg = body2.get("message", str(body2))
            log(f"⚠️ 创建仓库失败: {status2} {msg}")
            log("  可手动去 https://github.com/new 创建空私有仓库后再 init")
    else:
        log(f"⚠️ 检查仓库存在性失败: {status} {body.get('message', str(body))}")


def brain_sources():
    """返回 [(相对名, 本地路径), ...] —— 要同步的本机大脑文件。"""
    out = []
    s = APP / "skills"
    if s.exists():
        out.append(("skills", s))
    m = APP / "MEMORY.md"
    if m.exists():
        out.append(("MEMORY.md", m))
    md = APP / "memory"
    if md.exists():
        out.append(("memory", md))
    return out


def backup_target(dst):
    """覆盖前把目标备份到 _backup/<时间戳>。"""
    if not dst.exists():
        return
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bk = BACKUP / ts
    try:
        bk.mkdir(parents=True, exist_ok=True)
        if dst.is_dir():
            shutil.copytree(dst, bk / dst.name, ignore=IGNORE)
        else:
            shutil.copy2(dst, bk / dst.name)
        log(f"已备份 {dst.name} -> _backup/{ts}/")
    except Exception as e:
        log(f"备份失败(继续): {e}")


def copy_one(src, dst):
    """覆盖式复制单个源(文件或目录)到 dst, 应用忽略规则。"""
    if dst.exists():
        backup_target(dst)
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst, ignore=IGNORE)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def push_to(dst_root):
    dst_root = Path(dst_root)
    dst_root.mkdir(parents=True, exist_ok=True)
    for name, src in brain_sources():
        copy_one(src, dst_root / name)
    meta = dst_root / ".wbsync_meta.json"
    meta.write_text(
        json.dumps({"machine": MACHINE, "time": datetime.datetime.now().isoformat()},
                   ensure_ascii=False),
        encoding="utf-8",
    )


def pull_from(dst_root):
    dst_root = Path(dst_root)
    if not dst_root.exists():
        log("远端目录不存在, 无法 pull")
        return False
    for name, _src in brain_sources():
        s = dst_root / name
        if s.exists():
            copy_one(s, APP / name)
    return True


def git_available():
    return GIT_BIN is not None and Path(GIT_BIN).exists()


def run_git(args, check=True):
    r = subprocess.run([GIT_BIN] + args, cwd=GIT_REPO, env=git_env())
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败 (code {r.returncode})")
    return r.returncode


def ensure_repo(remote):
    """确保本地 .repo 缓存存在(不存在则 clone)。"""
    if GIT_REPO.exists() and (GIT_REPO / ".git").exists():
        return
    GIT_REPO.mkdir(parents=True, exist_ok=True)
    log(f"首次 clone 仓库到本地缓存 {GIT_REPO}")
    r = subprocess.run([GIT_BIN, "clone", remote, str(GIT_REPO)], env=git_env())
    if r.returncode != 0:
        log("clone 失败: 请检查 ①仓库 URL 是否正确 ②网络/代理可达 ③GitHub Desktop 是否已登录")
        raise RuntimeError("git clone 失败")


def _ignore_file(f):
    """变更检测时跳过的文件(与安全/缓存相关, 不参与同步比较)。"""
    if f.name in ("settings.json", "mcp.json"):
        return True
    if f.suffix == ".log":
        return True
    for part in f.parts:
        if part in ("node_modules", "__pycache__", ".git", "_backup", ".repo"):
            return True
    return False


def brain_hash():
    """对每个大脑源(技能/MEMORY.md/memory)计算内容哈希, 用于变更检测。"""
    h = {}
    for name, src in brain_sources():
        if src.is_dir():
            dig = hashlib.sha256()
            for f in sorted(src.rglob("*")):
                if f.is_file() and not _ignore_file(f):
                    dig.update(str(f.relative_to(src)).encode("utf-8"))
                    dig.update(f.read_bytes())
            h[name] = dig.hexdigest()
        elif src.exists():
            h[name] = hashlib.sha256(src.read_bytes()).hexdigest()
    return h


def load_manifest():
    try:
        if MANIFEST.exists():
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_manifest(h):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")


def cmd_auto(args):
    """变更检测: 仅当技能/MEMORY/memory 有新增或改动时才 push 到远端(发布端角色)。"""
    cur = brain_hash()
    prev = load_manifest()
    changed = {k: v for k, v in cur.items() if prev.get(k) != v}
    if not changed:
        log("无新增/改动技能, 跳过 push (与上次推送一致)")
        return
    names = ", ".join(changed.keys())
    log(f"检测到变更源: {names} -> 准备推送到远端")
    cmd_push(args)          # 走现有 git 流程(含 pull --rebase 以合并远端对方可能的新增)
    save_manifest(cur)
    log("已更新本地变更快照(.wb-sync/manifest.json)")


def cmd_init(args):
    cfg = load_cfg()
    cfg["remote_type"] = args.type
    cfg["remote"] = args.remote
    save_cfg(cfg)
    log(f"已配置远端: type={args.type}  remote={args.remote}")
    if args.type == "git":
        if not git_available():
            log("警告: 未检测到 git, 请先安装 Git 或 GitHub Desktop")
        else:
            log(f"使用 git: {GIT_BIN}")
            ensure_github_repo(args.remote)
            try:
                ensure_repo(args.remote)
                log("git 仓库已就绪")
            except RuntimeError as e:
                log(str(e))


def cmd_push(args):
    cfg = load_cfg()
    if not cfg.get("remote"):
        log("未配置远端, 先运行: python sync.py init --type git --remote <仓库URL>")
        return
    rt, remote = cfg["remote_type"], cfg["remote"]
    if rt == "folder":
        push_to(remote)
        log(f"已 push 到 {remote} (folder)")
    elif rt == "git":
        if not git_available():
            log("需要 git"); return
        try:
            ensure_repo(remote)
        except RuntimeError as e:
            log(str(e)); return
        # 检查远端是否已有 commit(空仓库首次 push 不能 pull)
        ls_remote = subprocess.run(
            [GIT_BIN, "ls-remote", "--heads", "origin", "main"],
            cwd=GIT_REPO, env=git_env(), capture_output=True, text=True, check=False
        )
        if ls_remote.returncode == 0 and ls_remote.stdout.strip():
            rc = run_git(["pull", "--rebase"], check=False)
            if rc != 0:
                log("pull --rebase 冲突或失败, 请检查网络/凭证, 或手动到 .repo 解决冲突"); return
        push_to(GIT_REPO)
        run_git(["add", "."])
        st = subprocess.run([GIT_BIN, "diff", "--cached", "--quiet"], cwd=GIT_REPO, env=git_env())
        if st.returncode != 0:
            # 空仓库首次没有 parent, 加 --allow-empty 确保能 commit
            run_git(["commit", "-m", f"wb-sync {MACHINE} {datetime.datetime.now().isoformat()}"])
            rc2 = run_git(["push", "-u", "origin", "main"], check=False)
            if rc2 != 0:
                log("push 失败: 检查凭证/网络后重试"); return
            log(f"已 push 到 git {remote}")
        else:
            log("本机无变更, 已拉取远端最新(无需 push)")


def cmd_pull(args):
    cfg = load_cfg()
    if not cfg.get("remote"):
        log("未配置远端, 先运行 init"); return
    rt, remote = cfg["remote_type"], cfg["remote"]
    if rt == "folder":
        meta = Path(remote) / ".wbsync_meta.json"
        if meta.exists():
            try:
                m = json.loads(meta.read_text(encoding="utf-8"))
                if m.get("machine") != MACHINE:
                    log(f"提示: 远端最后由 {m.get('machine')} 于 {m.get('time')} 更新。"
                         f"pull 将用远端覆盖本机, 覆盖前已自动备份。")
            except Exception:
                pass
        if not pull_from(remote):
            return
        log(f"已 pull 自 {remote} (folder)")
    elif rt == "git":
        if not git_available():
            log("需要 git"); return
        try:
            ensure_repo(remote)
        except RuntimeError as e:
            log(str(e)); return
        rc = run_git(["pull", "--rebase"], check=False)
        if rc != 0:
            log("pull 冲突或失败, 请检查网络/凭证, 或手动到 .repo 解决冲突"); return
        if not pull_from(GIT_REPO):
            return
        log(f"已 pull 自 git {remote}")


def count_files(p):
    if not p.exists():
        return 0
    if p.is_file():
        return 1
    return sum(1 for _ in p.rglob("*") if _.is_file() and _.name not in ("settings.json", "mcp.json")
               and not any(part in ("node_modules", "__pycache__", ".git", "_backup") for part in _.parts)
               and _.suffix != ".log")


def cmd_status(args):
    cfg = load_cfg()
    log(f"本机: {MACHINE}")
    log(f"大脑源: {[str(s) for _, s in brain_sources()]}")
    if not cfg.get("remote"):
        log("远端: 未配置 (运行 init 配置)"); return
    log(f"远端({cfg['remote_type']}): {cfg['remote']}")
    if cfg["remote_type"] == "folder":
        dst = Path(cfg["remote"])
        for name, _ in brain_sources():
            lc = count_files(APP / name)
            rc = count_files(dst / name)
            mark = "OK" if lc == rc else "差异"
            log(f"  {name}: 本机 {lc} 文件 / 远端 {rc} 文件  [{mark}]")
    else:
        log("git 模式: 运行 push/pull 后与远端对齐; 可用 `push`/`pull` 实际同步")


def cmd_doctor(args):
    cfg = load_cfg()
    log(f"本机: {MACHINE}")
    log(f"APP 目录: {APP}")
    log(f"git: {'可用' if git_available() else '未安装'} ({GIT_BIN})")
    log(f"代理: HTTPS_PROXY={os.environ.get('HTTPS_PROXY','未设置')}  HTTP_PROXY={os.environ.get('HTTP_PROXY','未设置')}")
    log(f"远端配置: {cfg.get('remote_type', '无')}  {cfg.get('remote', '')}")
    log(f"大脑源: {[str(s) for _, s in brain_sources()]}")


def main():
    p = argparse.ArgumentParser(prog="wb-sync", description="WorkBuddy 跨设备同步")
    sub = p.add_subparsers(dest="cmd")
    pi = sub.add_parser("init", help="配置中转远端")
    pi.add_argument("--type", required=True, choices=["folder", "git"])
    pi.add_argument("--remote", required=True, help="folder=共享目录; git=仓库 URL(支持 GitHub 自动创建)")
    pi.set_defaults(func=cmd_init)
    sub.add_parser("push", help="把本机大脑推到远端").set_defaults(func=cmd_push)
    sub.add_parser("pull", help="从远端拉回本机").set_defaults(func=cmd_pull)
    sub.add_parser("auto", help="变更检测: 仅新增/改动技能时才 push").set_defaults(func=cmd_auto)
    sub.add_parser("status", help="对比本机与远端").set_defaults(func=cmd_status)
    sub.add_parser("doctor", help="检查环境").set_defaults(func=cmd_doctor)
    args = p.parse_args()
    if not getattr(args, "cmd", None):
        p.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
