#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkBuddy 跨设备同步技能  (workbuddy-cross-device-sync)
把本机的"大脑"——用户级技能(~/.workbuddy/skills) + 用户级记忆(MEMORY.md)——
同步到另一台装了同技能的电脑,实现技能和记忆互通。

支持三种中转(在 init 时选择):
  - folder : 一个共享/同步盘目录(局域网 SMB 或 云盘同步空间),零外部依赖
  - git    : 一个 Git 仓库(推荐 GitHub 私有仓库, 跨网/跨地点通用)
  - api    : 直接用 GitHub REST API 操作私有仓库(无需 git 二进制,
             适合代理环境把 git 通道挡死、但 api.github.com 放行的场景,
             例如本机装了 GitHub Desktop 登录后令牌在钥匙串 macOS 上)

git 模式说明:
  - 优先使用 GitHub Desktop 自带 git, 自动复用它的登录态(无需手动 PAT/SSH)
  - remote 填仓库 URL(如 https://github.com/<你>/wb-skills-sync.git)
  - 首次 init 若 GitHub 仓库不存在, 会用登录态 token 自动创建私有仓库
  - 首次运行会自动 clone 到技能目录下的 .repo 缓存, 之后 pull/push 都走它
  - 走本机 env 里的 HTTPS_PROXY/HTTP_PROXY 代理(适配国内上网环境)

api 模式说明:
  - 自动从本机取 GitHub 令牌: macOS 钥匙串("GitHub - https://api.github.com")优先,
    Windows 走 git credential fill, 也可在 config.json 显式写 token。
  - 走 api.github.com(代理通常放行, 不像 git 的 CONNECT 隧道被挡)。
  - push 前会先 pull 合并远端(避免覆盖对方新增), 再上传本机全量并删除远端多余项。
  - 安全策略同 git: 永不碰 settings.json / mcp.json / 本机 config.json(机器本地配置)。

安全策略:
  - 排除 settings.json / mcp.json / config.json(含 API key / OAuth 令牌 / 本机 remote 配置, 每台机器独立, 绝不外传)
  - 排除 node_modules / __pycache__ / .git / _backup / *.log
  - 每次覆盖目标前自动备份到 _backup/<时间戳>, 可回滚
"""

import os
import sys
import re
import json
import base64
import shutil
import datetime
import argparse
import subprocess
import platform
import socket
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

APP = Path(os.environ.get("USERPROFILE", Path.home())) / ".workbuddy"
SKILL_DIR = Path(__file__).resolve().parent
CONFIG = SKILL_DIR / "config.json"
BACKUP = SKILL_DIR / "_backup"
GIT_REPO = APP / ".wb-sync" / "repo"   # git 模式本地缓存,放在 APP 下避免与技能目录互相嵌套
MANIFEST = APP / ".wb-sync" / "manifest.json"  # 本机上次推送的内容快照, 不随技能同步
MACHINE = (os.environ.get("COMPUTERNAME")
           or os.environ.get("HOSTNAME")
           or socket.gethostname()
           or platform.node()
           or "unknown")

# 同步时永远忽略的东西(本机配置/缓存/凭据)
IGNORE = shutil.ignore_patterns(
    "node_modules", "__pycache__", ".git", "_backup", ".repo",
    "*.log", "settings.json", "mcp.json", "config.json",
)
# 仅这些前缀的仓库文件参与同步(绝不碰 settings.json/mcp.json/config.json/其他根文件)
SYNC_PREFIX = ("skills/", "MEMORY.md", "memory/")


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
            # GitHub Desktop 新版把 git 放在 app 根目录
            app / "git" / "cmd" / "git.exe",
            app / "git" / "mingw64" / "bin" / "git.exe",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    return None


# 优先 GitHub Desktop 自带 git(复用登录态), 否则 fallback 系统 git
GIT_BIN = find_desktop_git() or shutil.which("git") or "git"


def git_base_args():
    """
    为系统 git 补强的全局参数。
    - 国内/代理环境下 openssl 常出现 TLS EOF, schannel 走 Windows 系统代理更稳。
    - 若系统 git 的 credential.helper 指向了不存在的 Desktop GCM 路径, 则改用自带 manager。
    """
    extras = ["-c", "http.sslbackend=schannel"]
    # 检查当前全局 credential.helper 是否指向一个已不存在的可执行文件
    try:
        r = subprocess.run(
            [GIT_BIN, "config", "--global", "credential.helper"],
            capture_output=True, text=True, timeout=10
        )
        helper = r.stdout.strip()
        if helper and not Path(helper).exists() and "credential-manager" in helper.lower():
            extras.extend(["-c", "credential.helper=manager"])
    except Exception:
        pass
    return extras


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
    """多策略获取 GitHub 令牌, 优先级: config.token > macOS 钥匙串 > git credential fill。"""
    # 1. 配置里显式指定的 token(可选)
    cfg = load_cfg()
    if cfg.get("token"):
        return cfg["token"].strip()
    # 2. macOS 钥匙串: GitHub Desktop / gh 存的 "GitHub - https://api.github.com"
    if platform.system() == "Darwin":
        for svc in ("GitHub - https://api.github.com", "github.com"):
            try:
                r = subprocess.run(
                    ["security", "find-generic-password", "-s", svc, "-w"],
                    capture_output=True, text=True, timeout=15,
                )
                if r.returncode == 0 and r.stdout.strip():
                    return r.stdout.strip()
            except Exception:
                pass
    # 3. Windows / 已配置 git credential 的机器: 走 git credential fill
    try:
        r = subprocess.run(
            [GIT_BIN] + git_base_args() + ["credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, env=git_env(), timeout=15,
        )
        if r.returncode == 0:
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")
    except Exception as e:
        return 0, {"error": str(e)}


# ---------------- API 模式核心 ----------------

def api_get_default_branch(token, owner, repo):
    status, body = github_api(token, f"https://api.github.com/repos/{owner}/{repo}")
    if status == 200 and isinstance(body, dict):
        return body.get("default_branch", "main")
    return "main"


def api_get_tree(token, owner, repo, branch):
    """递归获取仓库文件树, 返回 (tree_list, branch_used) 或 (None, branch)。"""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    status, body = github_api(token, url)
    if status == 200 and isinstance(body, dict) and "tree" in body:
        return body["tree"], branch
    # 默认分支可能不是传入的, 试一下 main/master
    for alt in ("main", "master"):
        if alt == branch:
            continue
        url2 = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{alt}?recursive=1"
        s2, b2 = github_api(token, url2)
        if s2 == 200 and isinstance(b2, dict) and "tree" in b2:
            return b2["tree"], alt
    return None, branch


def api_get_file(token, owner, repo, path, branch):
    """返回 (content_bytes, sha) 或 (None, None)。"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    status, body = github_api(token, url)
    if status == 200 and isinstance(body, dict) and "content" in body:
        try:
            data = base64.b64decode(body["content"])
            return data, body.get("sha")
        except Exception:
            return None, None
    return None, None


def api_put_file(token, owner, repo, path, content_bytes, sha=None, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    data = {
        "message": f"wb-sync {MACHINE}: put {path}",
        "content": base64.b64encode(content_bytes).decode("ascii"),
        "branch": branch,
    }
    if sha:
        data["sha"] = sha
    return github_api(token, url, "PUT", data)


def api_delete_file(token, owner, repo, path, sha, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    data = {"message": f"wb-sync {MACHINE}: delete {path}", "sha": sha, "branch": branch}
    return github_api(token, url, "DELETE", data)


def cmd_pull_api(token, owner, repo, branch):
    """从仓库拉 skills/MEMORY.md/memory 到本机(覆盖前自动备份)。返回是否成功。"""
    tree, branch = api_get_tree(token, owner, repo, branch)
    if tree is None:
        log("api pull 失败: 无法获取仓库文件树(检查令牌/仓库/网络)")
        return False
    files = [t for t in tree
             if t.get("type") == "blob"
             and t.get("path", "") not in ("settings.json", "mcp.json", "config.json")
             and t["path"].startswith(SYNC_PREFIX)]
    if not files:
        log("api pull: 仓库里没有可同步的大脑文件")
        return True
    ok = 0
    for t in files:
        p = t["path"]
        content, _ = api_get_file(token, owner, repo, p, branch)
        if content is None:
            log(f"  跳过(读不到): {p}")
            continue
        dst = APP / p
        if dst.exists():
            backup_target(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(content)
        ok += 1
        log(f"  已拉取: {p}")
    log(f"api pull 完成: 成功 {ok}/{len(files)} 个文件 (分支 {branch})")
    return True


def cmd_push_api(token, owner, repo, branch):
    """先合并远端(避免覆盖对方新增), 再把本机脑全量上传, 并删除远端多余项。"""
    # 1) 先 pull 合并远端到本机(幂等, 不删本机独有)
    cmd_pull_api(token, owner, repo, branch)
    # 2) 收集本机要同步的文件(排除 config.json 等本机配置)
    local_files = []
    for name, src in brain_sources():
        if src.is_dir():
            for f in sorted(src.rglob("*")):
                if f.is_file() and not _ignore_file(f):
                    local_files.append((str(f.relative_to(APP)), f.read_bytes()))
        elif src.exists():
            local_files.append((name, src.read_bytes()))
    local_paths = set(p for p, _ in local_files)
    # 3) 远端现有文件映射
    tree, branch = api_get_tree(token, owner, repo, branch)
    remote_files = {}
    if tree:
        for t in tree:
            if t.get("type") == "blob":
                remote_files[t["path"]] = t.get("sha")
    # 4) 上传/更新(并发, 控制节奏)
    def _put(item):
        p, data = item
        rsha = remote_files.get(p)
        st, b = api_put_file(token, owner, repo, p, data, sha=rsha, branch=branch)
        return p, st, b
    with ThreadPoolExecutor(max_workers=4) as ex:
        for p, st, b in ex.map(_put, local_files):
            if st in (200, 201):
                log(f"  已上传: {p}")
            else:
                msg = b.get("message", "") if isinstance(b, dict) else str(b)
                log(f"  上传失败 {p}: {st} {msg}")
    # 5) 删除远端有但本机没有的(双向一致; 仅同步范围内, 不碰 config.json)
    for rpath, rsha in remote_files.items():
        if rpath in ("settings.json", "mcp.json", "config.json"):
            continue
        if not rpath.startswith(SYNC_PREFIX):
            continue
        if rpath not in local_paths:
            st, b = api_delete_file(token, owner, repo, rpath, rsha, branch)
            log(f"  已删除远端多余: {rpath} ({st})")
    log(f"api push 完成 (分支 {branch})")
    return True


# ---------------- 通用(文件夹/git) ----------------

def ensure_github_repo(remote):
    """若 remote 是 GitHub 且仓库不存在, 用令牌自动创建私有仓库。"""
    owner, repo = parse_github_remote(remote)
    if not owner or not repo:
        return
    token = get_github_token()
    if not token:
        log("提示: 未获取到 GitHub 令牌, 请确认 GitHub Desktop 已登录或 config.json 已配置 token; 跳过自动创建仓库")
        return
    # 检查仓库是否存在
    status, body = github_api(token, f"https://api.github.com/repos/{owner}/{repo}")
    if status == 200:
        log(f"GitHub 仓库 {owner}/{repo} 已存在")
        return
    if status == 404:
        log(f"仓库 {owner}/{repo} 不存在, 正在用当前令牌自动创建私有仓库...")
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
    r = subprocess.run([GIT_BIN] + git_base_args() + args, cwd=GIT_REPO, env=git_env())
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败 (code {r.returncode})")
    return r.returncode


def ensure_repo(remote):
    """确保本地 .repo 缓存存在(不存在则 clone)。"""
    if GIT_REPO.exists() and (GIT_REPO / ".git").exists():
        return
    GIT_REPO.mkdir(parents=True, exist_ok=True)
    log(f"首次 clone 仓库到本地缓存 {GIT_REPO}")
    r = subprocess.run([GIT_BIN] + git_base_args() + ["clone", remote, str(GIT_REPO)], env=git_env())
    if r.returncode != 0:
        log("clone 失败: 请检查 ①仓库 URL 是否正确 ②网络/代理可达 ③GitHub Desktop 是否已登录")
        raise RuntimeError("git clone 失败")


def _ignore_file(f):
    """变更检测时跳过的文件(与安全/缓存/本机配置相关, 不参与同步比较)。"""
    if f.name in ("settings.json", "mcp.json", "config.json"):
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
    """变更检测: 先合并远端, 仅当技能/MEMORY/memory 有新增或改动时才 push 到远端(发布端角色)。"""
    cfg = load_cfg()
    rt = cfg.get("remote_type")
    # 先合并远端(幂等), 保证后续哈希比较准确
    if rt == "git":
        try:
            ensure_repo(cfg["remote"])
            run_git(["pull", "--rebase"], check=False)
        except Exception as e:
            log(f"合并远端失败(继续): {e}")
    elif rt == "api":
        token = get_github_token()
        if not token:
            log("未获取到 GitHub 令牌, 无法合并远端"); return
        owner, repo = parse_github_remote(cfg["remote"])
        if not owner:
            log("remote 解析失败"); return
        branch = api_get_default_branch(token, owner, repo)
        cmd_pull_api(token, owner, repo, branch)
    elif rt == "folder":
        pull_from(cfg["remote"])

    cur = brain_hash()
    prev = load_manifest()
    changed = {k: v for k, v in cur.items() if prev.get(k) != v}
    if not changed:
        log("无新增/改动, 跳过 push (与上次同步一致)")
        return
    names = ", ".join(changed.keys())
    log(f"检测到变更源: {names} -> 准备推送到远端")
    cmd_push(args)
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
    elif args.type == "api":
        token = get_github_token()
        if not token:
            log("警告: 未获取到 GitHub 令牌(请确认 GitHub Desktop 已登录 / macOS 钥匙串有条目 / 或 config.json 配置 token)")
        else:
            owner, repo = parse_github_remote(args.remote)
            if owner:
                branch = api_get_default_branch(token, owner, repo)
                status, body = github_api(token, f"https://api.github.com/repos/{owner}/{repo}")
                if status == 200:
                    log(f"✅ 令牌有效, 仓库 {owner}/{repo} 可访问 (默认分支 {branch})")
                elif status == 404:
                    log(f"仓库 {owner}/{repo} 不存在, 可用令牌自动创建私有仓库(运行 push 时创建)")
                else:
                    log(f"⚠️ 检查仓库失败: {status} {body.get('message','') if isinstance(body,dict) else body}")
            else:
                log("警告: 无法解析 remote 为 GitHub 仓库 URL")
    elif args.type == "folder":
        if not Path(args.remote).exists():
            log(f"提示: 共享目录 {args.remote} 不存在, 首次 push 时会创建")


def cmd_push(args):
    cfg = load_cfg()
    if not cfg.get("remote"):
        log("未配置远端, 先运行: python sync.py init --type api --remote <仓库URL>")
        return
    rt, remote = cfg["remote_type"], cfg["remote"]
    if rt == "folder":
        push_to(remote)
        log(f"已 push 到 {remote} (folder)")
    elif rt == "api":
        token = get_github_token()
        if not token:
            log("未获取到 GitHub 令牌, 无法 push"); return
        owner, repo = parse_github_remote(remote)
        if not owner:
            log("remote 解析失败"); return
        branch = api_get_default_branch(token, owner, repo)
        if not api_get_tree(token, owner, repo, branch)[0]:
            # 仓库可能为空, 确保存在
            ensure_github_repo(remote)
        cmd_push_api(token, owner, repo, branch)
    elif rt == "git":
        if not git_available():
            log("需要 git"); return
        try:
            ensure_repo(remote)
        except RuntimeError as e:
            log(str(e)); return
        ls_remote = subprocess.run(
            [GIT_BIN] + git_base_args() + ["ls-remote", "--heads", "origin", "main"],
            cwd=GIT_REPO, env=git_env(), capture_output=True, text=True, check=False
        )
        if ls_remote.returncode == 0 and ls_remote.stdout.strip():
            rc = run_git(["pull", "--rebase"], check=False)
            if rc != 0:
                log("pull --rebase 冲突或失败, 请检查网络/凭证, 或手动到 .repo 解决冲突"); return
        push_to(GIT_REPO)
        run_git(["add", "."])
        st = subprocess.run([GIT_BIN] + git_base_args() + ["diff", "--cached", "--quiet"], cwd=GIT_REPO, env=git_env())
        if st.returncode != 0:
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
    elif rt == "api":
        token = get_github_token()
        if not token:
            log("未获取到 GitHub 令牌, 无法 pull"); return
        owner, repo = parse_github_remote(remote)
        if not owner:
            log("remote 解析失败"); return
        branch = api_get_default_branch(token, owner, repo)
        if not cmd_pull_api(token, owner, repo, branch):
            return
        log(f"已 pull 自 git(api) {remote}")
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
    return sum(1 for _ in p.rglob("*") if _.is_file() and _.name not in ("settings.json", "mcp.json", "config.json")
               and not any(part in ("node_modules", "__pycache__", ".git", "_backup") for part in _.parts)
               and _.suffix != ".log")


def cmd_status(args):
    cfg = load_cfg()
    log(f"本机: {MACHINE}  (平台 {platform.system()})")
    log(f"大脑源: {[str(s) for _, s in brain_sources()]}")
    if not cfg.get("remote"):
        log("远端: 未配置 (运行 init 配置)"); return
    rt, remote = cfg["remote_type"], cfg["remote"]
    log(f"远端({rt}): {remote}")
    if rt == "folder":
        dst = Path(remote)
        for name, _ in brain_sources():
            lc = count_files(APP / name)
            rc = count_files(dst / name)
            mark = "OK" if lc == rc else "差异"
            log(f"  {name}: 本机 {lc} 文件 / 远端 {rc} 文件  [{mark}]")
    elif rt == "api":
        token = get_github_token()
        if not token:
            log("  令牌: 未获取到(无法比对远端)"); return
        owner, repo = parse_github_remote(remote)
        if not owner:
            log("  remote 解析失败"); return
        branch = api_get_default_branch(token, owner, repo)
        tree, _ = api_get_tree(token, owner, repo, branch)
        if tree is None:
            log("  无法获取远端树(检查网络/令牌)"); return
        remote_paths = set(t["path"] for t in tree if t["type"] == "blob"
                           and t["path"].startswith(SYNC_PREFIX))
        local_paths = set()
        for name, src in brain_sources():
            if src.is_dir():
                for f in src.rglob("*"):
                    if f.is_file() and not _ignore_file(f):
                        local_paths.add(str(f.relative_to(APP)))
            elif src.exists():
                local_paths.add(name)
        only_local = local_paths - remote_paths
        only_remote = remote_paths - local_paths
        log(f"  远端可同步文件数: {len(remote_paths)}  本机可同步文件数: {len(local_paths)}")
        if only_local:
            log(f"  仅本机有(下次 push 会上传): {len(only_local)} 个")
        if only_remote:
            log(f"  仅远端有(下次 pull 会下载): {len(only_remote)} 个")
        if not only_local and not only_remote:
            log("  本机与远端一致 ✅")
    else:
        log("git 模式: 运行 push/pull 后与远端对齐; 可用 `push`/`pull` 实际同步")


def cmd_doctor(args):
    cfg = load_cfg()
    log(f"本机: {MACHINE}  (平台 {platform.system()})")
    log(f"APP 目录: {APP}")
    log(f"git: {'可用' if git_available() else '未安装'} ({GIT_BIN})")
    log(f"代理: HTTPS_PROXY={os.environ.get('HTTPS_PROXY','未设置')}  HTTP_PROXY={os.environ.get('HTTP_PROXY','未设置')}")
    tk = get_github_token()
    log(f"GitHub 令牌: {'已获取' if tk else '未获取'} ({'len='+str(len(tk)) if tk else 'None'})")
    log(f"远端配置: {cfg.get('remote_type', '无')}  {cfg.get('remote', '')}")
    log(f"大脑源: {[str(s) for _, s in brain_sources()]}")


def main():
    p = argparse.ArgumentParser(prog="wb-sync", description="WorkBuddy 跨设备同步")
    sub = p.add_subparsers(dest="cmd")
    pi = sub.add_parser("init", help="配置中转远端")
    pi.add_argument("--type", required=True, choices=["folder", "git", "api"])
    pi.add_argument("--remote", required=True, help="folder=共享目录; git/api=仓库 URL(支持 GitHub 自动创建)")
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
