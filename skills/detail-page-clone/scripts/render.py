#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render.py — 把 build.py 生成的 HTML 截图成详情长图，并按平台上限安全切图。

零第三方浏览器依赖：自动探测本机 Edge / Chrome，用 headless 模式截图。
仅切图功能需要 Pillow（已装在受管 venv 里）。

用法:
  python render.py --html build/index.html --platform taobao --out out/
  python render.py --html build/index.html --out out/ --format jpg --quality 90 --slice
  python render.py --html build/index.html --out out/ --spec style-spec.json --slice-height 1800
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PLATFORMS = {
    "taobao":    {"w": 750,  "max_h": 2000, "min_fs": 24},
    "pdd":       {"w": 750,  "max_h": 2500, "min_fs": 28},
    "douyin":    {"w": 1080, "max_h": 1920, "min_fs": 32},
    "kuaishou":  {"w": 1080, "max_h": 1920, "min_fs": 32},
    "jd":        {"w": 990,  "max_h": 2000, "min_fs": 24},
}

MAX_WINDOW_H = 16000  # Chrome headless 稳定上限


def find_browser():
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    for name in ("chrome", "msedge", "chromium", "google-chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def screenshot(browser, html_path: Path, out_png: Path, width: int, height_hint: int):
    h = min(max(height_hint, 2000), MAX_WINDOW_H)
    url = html_path.resolve().as_uri()
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        "--force-device-scale-factor=1",
        "--disable-lcd-text",
        f"--window-size={width},{h}",
        "--virtual-time-budget=10000",
        f"--screenshot={str(out_png)}",
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if not out_png.exists():
        sys.stderr.write(r.stdout.decode("utf-8", "ignore")[-2000:])
        sys.stderr.write(r.stderr.decode("utf-8", "ignore")[-2000:])
        raise RuntimeError("截图失败，浏览器未产出文件")
    return out_png


def _bottom_has_content(rgb, tol=8):
    """截图最后几行是否有内容 —— 有则说明页面被窗口截断。"""
    w, h = rgb.size
    bg = rgb.getpixel((2, 2))
    step = max(1, w // 80)
    for y in range(max(0, h - 3), h):
        for x in range(0, w, step):
            p = rgb.getpixel((x, y))
            if any(abs(p[i] - bg[i]) > tol for i in range(3)):
                return True
    return False


def _row_is_uniform(rgb, y, w, step, tol=6):
    """判断第 y 行是否水平纯色（可变背景色模块里也能识别为安全切割行）。"""
    first = rgb.getpixel((0, y))
    for x in range(step, w, step):
        p = rgb.getpixel((x, y))
        if any(abs(p[i] - first[i]) > tol for i in range(3)):
            return False
    return True


def trim_bottom(im, pad=0, tol=8, need=50):
    """裁掉截图窗口底部连续 need 行的纯色空白（典型场景：Chrome 窗口比页面高）。

    从最底部往上扫：只要遇到第一行非纯色就停，最底部必须有连续 need 行空白才裁。
    避免误裁"深色模块末尾也是纯色"的情况——那种情况下 cut_y = h，不裁。
    """
    try:
        from PIL import Image
    except ImportError:
        return im, 0
    rgb = im.convert("RGB")
    w, h = rgb.size
    step = max(1, w // 80)
    cur_run = 0
    cut_y = h
    for y in range(h - 1, -1, -1):
        if _row_is_uniform(rgb, y, w, step, tol):
            cur_run += 1
        else:
            if cur_run >= need:
                cut_y = y + 1
            break
    cut = min(h, cut_y + pad)
    if cut < h:
        im = im.crop((0, 0, w, cut))
    return im, cut


def find_safe_cut(rgb, y_target, lo, hi, need_blank=10, tol=6):
    """在 [lo, hi) 内找连续 need_blank 行的水平纯色带，返回最接近 y_target 的 y。

    用"行内颜色均匀"而非"等于某个背景色"来判断，
    这样在米色/深色/渐变模块内部也能找到安全切割点。
    """
    w, h = rgb.size
    lo = max(0, lo)
    hi = min(h, hi)
    if hi <= lo:
        return None
    step = max(1, w // 100)

    runs = []
    run_start = None
    for y in range(lo, hi):
        if _row_is_uniform(rgb, y, w, step, tol):
            if run_start is None:
                run_start = y
        else:
            if run_start is not None and y - run_start >= need_blank:
                runs.append((run_start + y) // 2)
            run_start = None
    if run_start is not None and hi - run_start >= need_blank:
        runs.append((run_start + hi) // 2)
    if not runs:
        return None
    return min(runs, key=lambda y: abs(y - y_target))


def slice_image(img_path: Path, out_dir: Path, max_h: int, names, fmt, quality):
    try:
        from PIL import Image
    except ImportError:
        print("[ERR] 切图需要 Pillow，请先安装：pip install Pillow")
        return []
    im = Image.open(img_path)
    w, h = im.size
    rgb = im.convert("RGB")
    if h <= max_h:
        out = out_dir / f"01{names[0] if names else ''}.{fmt}"
        save_img(im, out, fmt, quality)
        print(f"[OK] 无需切图 -> {out.name}  ({w}x{h})")
        return [out]

    pieces = []
    y = 0
    i = 0
    while y < h:
        target = y + max_h
        flag = None
        if target >= h:
            end = h
        else:
            # 优先在 [target - 15%, target] 找安全切割点（避免超出 max_h 上限）
            lo = int(target - max_h * 0.15)
            hi = target
            cut = find_safe_cut(rgb, target, lo, hi)
            if cut is None:
                # 退而求其次：扩到 [target, target + 10%]，但最终 cap 到 target（不超 max_h）
                cut = find_safe_cut(rgb, target, target, int(target + max_h * 0.10))
                if cut is None or cut > target:
                    cut = target
                    flag = "risk"
            end = cut
        box = im.crop((0, y, w, end))
        nm = names[i] if i < len(names) else f"{i+1:02d}"
        suffix = f"{i+1:02d}{nm}"
        out = out_dir / f"{suffix}.{fmt}"
        save_img(box, out, fmt, quality)
        pieces.append(out)
        if flag == "risk":
            print(f"[WARN] 第 {i+1} 段未找到安全切割点，可能切断文字：y={end}")
        y = end
        i += 1
    return pieces


def save_img(im, out: Path, fmt, quality):
    if fmt == "jpg":
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGB")
        im.save(out, "JPEG", quality=quality, optimize=True, subsampling=0)
    else:
        im.save(out, "PNG", optimize=True)


def main():
    ap = argparse.ArgumentParser(description="HTML -> 详情长图 + 安全切图")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--platform", default="taobao")
    ap.add_argument("--spec", default=None, help="用于按模块 id 命名切图")
    ap.add_argument("--format", default="png", choices=["png", "jpg"])
    ap.add_argument("--quality", type=int, default=90)
    ap.add_argument("--slice", action="store_true", help="按平台上限切图")
    ap.add_argument("--slice-height", type=int, default=None, help="自定义单图高度上限")
    ap.add_argument("--height-hint", type=int, default=12000, help="预估整页高度，用于设置截图窗口")
    ap.add_argument("--browser", default=None, help="手动指定浏览器路径")
    a = ap.parse_args()

    plat = PLATFORMS.get(a.platform, PLATFORMS["taobao"])
    html_p = Path(a.html).resolve()
    out_dir = Path(a.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    browser = a.browser or find_browser()
    if not browser:
        print("[ERR] 未找到 Edge / Chrome。请用 --browser 指定路径，或手动打开 HTML 用浏览器截图。")
        print(f"      HTML 已生成：{html_p}")
        sys.exit(2)
    print(f"[..] 使用浏览器：{browser}")

    tmp_png = out_dir / "_full_raw.png"
    hint = a.height_hint
    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        has_pil = False

    while True:
        win_h = min(max(hint, 2000), MAX_WINDOW_H)
        screenshot(browser, html_p, tmp_png, plat["w"], hint)
        if not has_pil:
            break
        with Image.open(tmp_png) as probe:
            reached = _bottom_has_content(probe.convert("RGB"))
        if not reached or win_h >= MAX_WINDOW_H:
            break
        nxt = min(win_h * 2, MAX_WINDOW_H)
        if nxt <= win_h:
            break
        print(f"[..] 页面超出截图窗口（{win_h}px），自动放大到 {nxt}px 重试")
        hint = nxt
    print("[OK] 整页截图完成")

    # 裁剪底部空白
    try:
        from PIL import Image
        im = Image.open(tmp_png)
        im, cut = trim_bottom(im, pad=0)
        full = out_dir / f"00_full.{a.format}"
        save_img(im, full, a.format, a.quality)
        print(f"[OK] 整图 -> {full.name}  ({im.size[0]}x{im.size[1]})")
        if im.size[1] >= MAX_WINDOW_H - 5:
            print(f"[WARN] 页面高度达到截图窗口上限（{MAX_WINDOW_H}px），可能被截断。")
            print("       请用 --height-hint 调小单页内容，或把详情图拆成多段分别渲染。")
    except ImportError:
        full = tmp_png.rename(out_dir / f"00_full.{a.format}")
        print(f"[OK] 整图 -> {full.name}（未裁剪底部空白，Pillow 未安装）")
        if not a.slice:
            return

    if a.slice:
        names = []
        if a.spec and Path(a.spec).exists():
            sp = json.loads(Path(a.spec).read_text(encoding="utf-8"))
            ov = {}
            names = ["_" + m.get("id", f"{i+1:02d}") for i, m in enumerate(sp.get("modules", []))]
        max_h = a.slice_height or plat["max_h"]
        pieces = slice_image(full, out_dir, max_h, names, a.format, a.quality)
        print(f"[OK] 切图完成，共 {len(pieces)} 张，上限 {max_h}px")


if __name__ == "__main__":
    main()
