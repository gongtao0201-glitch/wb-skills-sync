#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 把 style-spec.json（版式骨架）+ content.json（产品内容）渲染成单个 HTML。

用法:
  python build.py --spec style-spec.json --content content.json --out build/index.html
  python build.py --spec style-spec.json --content content.json --out build/index.html --platform pdd

输出:
  单个自包含 HTML（CSS 内联、图片转 file:// 绝对地址），可直接被 render.py 截图。
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
BASE_CSS = SKILL_DIR / "assets" / "base.css"

# 平台预设：基准宽 750，单图高上限，最小字号
PLATFORMS = {
    "taobao":    {"w": 750,  "max_h": 2000, "min_fs": 24},
    "pdd":       {"w": 750,  "max_h": 2500, "min_fs": 28},
    "douyin":    {"w": 1080, "max_h": 1920, "min_fs": 32},
    "kuaishou":  {"w": 1080, "max_h": 1920, "min_fs": 32},
    "jd":        {"w": 990,  "max_h": 2000, "min_fs": 24},
}
BASE_W = 750

VAR_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_.\-]+)\s*\}\}")


# ---------------------------------------------------------------- 工具
def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def to_uri(p: str, base_dir: Path) -> str:
    """把相对图片路径转成 file:// 绝对地址，缺文件原样返回。"""
    if not p:
        return ""
    if re.match(r"^(https?:|data:|file:)", p):
        return p
    cand = (base_dir / p)
    if not cand.exists():
        cand = Path(p)
    if not cand.exists():
        return p
    return cand.resolve().as_uri()


def subst(v, ctx):
    """递归替换字符串里的 {{变量}}。"""
    if isinstance(v, str):
        def rep(m):
            key = m.group(1)
            return str(ctx.get(key, m.group(0)))  # 找不到就保留原样，交给 qa_check 报
        return VAR_RE.sub(rep, v)
    if isinstance(v, list):
        return [subst(i, ctx) for i in v]
    if isinstance(v, dict):
        return {k: subst(x, ctx) for k, x in v.items()}
    return v


def get(slots, key, default=""):
    return slots.get(key, default) if isinstance(slots, dict) else default


def esc(s):
    return html.escape(str(s), quote=True)


def render_title(slot, tag="h2", default_role=None):
    """支持 parts 数组、accent_word、accent_char 多种形式，输出多色标题。

    slot 取值形态：
      - str:                                   直接输出
      - {"text": ..., "role": "section_title"} 整段一个色
      - {"text": ..., "accent_word": ..., "accent_color": ...}  关键词着色
      - {"text": ..., "accent_char": "！", "accent_color": ...} 字符着色
      - {"parts": [{"text","color","size","role"}, ...]}         分段着色
    """
    if slot is None or slot == "":
        return ""
    if isinstance(slot, str):
        text = slot
        color = None
        accent = None
        accent_color = None
        accent_char = None
        parts = None
    elif isinstance(slot, dict):
        parts = slot.get("parts")
        if parts:
            out = []
            for p in parts:
                t = str(p.get("text", ""))
                style_parts = []
                if p.get("color"):
                    style_parts.append(f"color:{p['color']}")
                if p.get("size"):
                    style_parts.append(f"font-size:{p['size']}px")
                sty = f' style="{";".join(style_parts)}"' if style_parts else ""
                # 行内 \n 转 <br>
                if "\n" in t:
                    chunks = t.split("\n")
                    inner = ""
                    for i, ch in enumerate(chunks):
                        if i:
                            inner += "<br>"
                        inner += esc(ch)
                    out.append(f"<span{sty}>{inner}</span>")
                else:
                    out.append(f"<span{sty}>{esc(t)}</span>")
            joined = "".join(out)
            cls = slot.get("role") or default_role
            cls_attr = f' class="{cls}"' if cls else ""
            return f"<{tag}{cls_attr}>{joined}</{tag}>"
        text = slot.get("text", "")
        color = slot.get("color")
        accent = slot.get("accent_word")
        accent_color = slot.get("accent_color")
        accent_char = slot.get("accent_char")
    else:
        text = str(slot)
        color = accent = accent_color = accent_char = None
        parts = None

    role = (isinstance(slot, dict) and slot.get("role")) or default_role
    cls_attr = f' class="{role}"' if role else ""
    sty_attr = ""

    # 关键词着色
    target = accent or accent_char
    if accent_color and target and target in text:
        # 全局只替换第一个匹配；accent_char 着色完整字符，accent_word 着色完整词
        t1, t2 = text.split(target, 1)
        sty_color = f' style="color:{color}"' if color else ""
        return (
            f"<{tag}{cls_attr}{sty_color}>"
            f"{esc(t1)}<span style=\"color:{accent_color}\">{esc(target)}</span>{esc(t2)}"
            f"</{tag}>"
        )

    if color:
        sty_attr = f' style="color:{color}"'
    return f"<{tag}{cls_attr}{sty_attr}>{esc(text)}</{tag}>"


# ---------------------------------------------------------------- CSS 变量
def scale_val(v, scale):
    """把 '72px' / '0.02em' / '8px 20px' 里的 px 数值按比例缩放。"""
    if isinstance(v, (int, float)):
        return f"{round(v * scale)}px"
    s = str(v)

    def rep(m):
        return f"{round(float(m.group(1)) * scale)}px"
    return re.sub(r"(-?\d+(?:\.\d+)?)px", rep, s)


def build_css_vars(spec, scale, min_fs, warnings):
    pal = spec.get("palette", {})
    typ = spec.get("typography", {})
    dec = spec.get("decor", {})
    meta = spec.get("meta", {})
    lines = []

    lines.append(f"  --w: {round(BASE_W * scale)}px;")

    pal_map = {
        "primary": "--c-primary", "secondary": "--c-secondary", "accent": "--c-accent",
        "bg_base": "--c-bg-base", "bg_alt": "--c-bg-alt",
        "text_main": "--c-text-main", "text_sub": "--c-text-sub",
        "text_inverse": "--c-text-inverse", "line": "--c-line",
    }
    for k, cssv in pal_map.items():
        if pal.get(k):
            lines.append(f"  {cssv}: {pal[k]};")

    if typ.get("font_stack"):
        lines.append(f"  --ff-base: {typ['font_stack']};")
    if typ.get("title_font_stack"):
        lines.append(f"  --ff-title: {typ['title_font_stack']};")
    else:
        lines.append(f"  --ff-title: {typ.get('font_stack', 'inherit')};")

    # 字阶
    for item in typ.get("scale", []):
        role = item.get("role")
        if not role:
            continue
        p = f"--{role}"
        fs = item.get("size_px")
        if fs is not None:
            scaled = round(float(fs) * scale)
            if scaled < min_fs:
                warnings.append(f"[WARN] 字阶 {role} 由 {scaled}px 抬升至 {min_fs}px（平台下限）")
                scaled = min_fs
            lines.append(f"  {p}-size: {scaled}px;")
            lines.append(f"  --fs-{role}: var({p}-size);")
            lines.append(f"  --fw-{role}: {item.get('weight', 400)};")
            lines.append(f"  --fc-{role}: {item.get('color', 'inherit')};")
            lines.append(f"  --ls-{role}: {item.get('letter_spacing', 'normal')};")
            lines.append(f"  --lh-{role}: {item.get('line_height', 'normal')};")
            align = item.get("align")
            if align:
                lines.append(f"  --ta-{role}: {align};")

    # 装饰
    badge = dec.get("badge", {})
    if badge.get("bg"):
        lines.append(f"  --badge-bg: {badge['bg']};")
    if badge.get("radius_px") is not None:
        lines.append(f"  --badge-radius: {scale_val(badge['radius_px'], scale)};")
    if badge.get("padding"):
        lines.append(f"  --badge-pad: {scale_val(badge['padding'], scale)};")

    card = dec.get("card", {})
    if card.get("bg"):
        lines.append(f"  --card-bg: {card['bg']};")
    if card.get("radius_px") is not None:
        lines.append(f"  --card-radius: {scale_val(card['radius_px'], scale)};")
    if card.get("padding_px") is not None:
        lines.append(f"  --card-pad: {scale_val(card['padding_px'], scale)};")
    if card.get("shadow"):
        lines.append(f"  --card-shadow: {card['shadow']};")

    idx = dec.get("index_number", {})
    if idx.get("size_px") is not None:
        lines.append(f"  --idx-size: {scale_val(idx['size_px'], scale)};")
    if idx.get("bg"):
        lines.append(f"  --idx-bg: {idx['bg']};")
    if idx.get("color"):
        lines.append(f"  --idx-color: {idx['color']};")

    grad = dec.get("gradient", {})
    if grad:
        lines.append(f"  --grad-from: {grad.get('from', '#FFFFFF')};")
        lines.append(f"  --grad-to: {grad.get('to', '#FFFFFF')};")
        lines.append(f"  --grad-deg: {grad.get('deg', 180)}deg;")

    if dec.get("product_shadow"):
        lines.append(f"  --prod-shadow: {dec['product_shadow']};")

    return "\n".join(lines)


# ---------------------------------------------------------------- 模块渲染
def sec_head(slot, sub_slot=None, ctx=None):
    """统一处理章节标题 + 副标。支持 parts 数组、accent_word 等多色标题。"""
    if ctx is not None:
        if slot is not None and slot != "":
            slot = subst(slot, ctx)
        if sub_slot is not None and sub_slot != "":
            sub_slot = subst(sub_slot, ctx)
    out = ['<div class="sec-head">']
    if slot:
        out.append(render_title(slot, tag="h2"))
    if sub_slot:
        out.append(render_title(sub_slot, tag="p"))
    out.append("</div>")
    return "\n".join(out)


def render_hero(m, ctx):
    s = m.get("slots", {})
    h = m.get("height_px", 1000)
    bg = m.get("bg", "var(--c-bg-alt)")
    variant = m.get("variant", "")
    vcls = " variant-split" if variant == "split" else ""
    prod = s.get("product", {}) or {}
    src = to_uri(prod.get("src", ""), ctx["__base__"])
    scale_pct = prod.get("scale_pct", 55)
    pts = s.get("points", {}) or {}
    items = pts.get("items", []) if isinstance(pts, dict) else pts

    lis = "".join(f'<li class="badge">{esc(i)}</li>' for i in items if i)
    img = f'<img class="hero-product" src="{esc(src)}" style="--scale:{float(scale_pct)/100}">' if src else ""

    scene = s.get("scene_accent", {}) or {}
    scene_src = to_uri(scene.get("src", ""), ctx["__base__"])
    scene_html = f'<img class="hero-scene" src="{esc(scene_src)}">' if scene_src else ""

    title_html = render_title(s.get("title", ""), tag="h1", default_role="t-hero_title")
    sub_html = render_title(s.get("sub", ""), tag="p", default_role="t-hero_sub")

    return f"""<section class="mod mod-hero{vcls}" data-mod="hero" style="--h:{scale_val(h, ctx['__scale__'])};background:{bg}">
  <div class="hero-top">
    {title_html}
    {sub_html}
  </div>
  <div class="hero-visual">{img}{scene_html}</div>
  <ul class="hero-points">{lis}</ul>
</section>"""


def render_pain(m, ctx):
    s = m.get("slots", {})
    items = subst(s.get("items", []), ctx)
    cells = "".join(
        f'<div class="pain-item"><div class="idx">{i+1}</div><p class="t-body">{esc(it if isinstance(it,str) else it.get("text",""))}</p></div>'
        for i, it in enumerate(items)
    )
    return f"""<section class="mod mod-pain" data-mod="pain_point">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  <div class="pain-grid">{cells}</div>
</section>"""


def render_fgrid(m, ctx):
    s = m.get("slots", {})
    cols = s.get("cols", 2)
    items = subst(s.get("items", []), ctx)
    cards = []
    for it in items:
        if isinstance(it, str):
            it = {"title": it}
        img = to_uri(it.get("img", ""), ctx["__base__"])
        imgtag = f'<div class="card-img"><img src="{esc(img)}"></div>' if img else ""
        cards.append(
            f'<div class="card">{imgtag}'
            f'<h3 class="t-point_title">{esc(it.get("title",""))}</h3>'
            f'<p class="t-body">{esc(it.get("desc",""))}</p></div>'
        )
    return f"""<section class="mod mod-fgrid" data-mod="feature_grid">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  <div class="grid grid-{cols}">{''.join(cards)}</div>
</section>"""


def render_flist(m, ctx):
    s = m.get("slots", {})
    items = subst(s.get("items", []), ctx)
    rows = []
    for i, it in enumerate(items):
        if isinstance(it, str):
            it = {"title": it}
        img = to_uri(it.get("img", ""), ctx["__base__"])
        imgtag = f'<div class="row-img"><img src="{esc(img)}"></div>' if img else ""
        rows.append(
            f'<div class="row" data-flip="{"true" if i%2 else "false"}">{imgtag}'
            f'<div class="row-txt"><div class="idx">{i+1}</div>'
            f'<h3 class="t-point_title">{esc(it.get("title",""))}</h3>'
            f'<p class="t-body">{esc(it.get("desc",""))}</p></div></div>'
        )
    return f"""<section class="mod flist" data-mod="feature_list">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  {''.join(rows)}
</section>"""


def render_table(m, ctx):
    s = m.get("slots", {})
    rows = subst(s.get("rows", []), ctx)
    trs = []
    for r in rows:
        if isinstance(r, dict):
            k, v = r.get("k", ""), r.get("v", "")
        else:
            k, v = (r + [None, None])[:2] if isinstance(r, list) else ("", str(r))
        trs.append(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>")
    return f"""<section class="mod mod-table" data-mod="param_table">
  {sec_head(s.get('title','产品参数'), s.get('sub',''), ctx)}
  <table class="pt">{''.join(trs)}</table>
</section>"""


def render_proof(m, ctx):
    s = m.get("slots", {})
    items = subst(s.get("items", []), ctx)
    vcls = " variant-light" if m.get("variant") == "light" else ""
    cells = []
    for it in items:
        if isinstance(it, str):
            it = {"value": it}
        cells.append(
            f'<div class="proof-item">'
            f'<div class="t-number">{esc(it.get("value",""))}</div>'
            f'<div class="t-caption">{esc(it.get("unit",""))}</div>'
            f'<p class="t-body">{esc(it.get("desc",""))}</p></div>'
        )
    return f"""<section class="mod mod-proof{vcls}" data-mod="proof_data">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  <div class="proof-row">{''.join(cells)}</div>
</section>"""


def render_compare(m, ctx):
    s = m.get("slots", {})
    rows = subst(s.get("rows", []), ctx)
    us = subst(s.get("us_label", "本品"), ctx)
    oth = subst(s.get("other_label", "普通款"), ctx)
    dim = subst(s.get("dim_label", "对比项"), ctx)
    trs = []
    for r in rows:
        if isinstance(r, dict):
            trs.append(
                f'<tr><td class="cmp-dim">{esc(r.get("dim",""))}</td>'
                f'<td class="yes">{esc(r.get("us",""))}</td>'
                f'<td class="no">{esc(r.get("other",""))}</td></tr>'
            )
    return f"""<section class="mod mod-compare" data-mod="compare">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  <table class="cmp">
    <thead><tr><th class="cmp-dim">{esc(dim)}</th><th class="cmp-us">{esc(us)}</th><th class="cmp-oth">{esc(oth)}</th></tr></thead>
    <tbody>{''.join(trs)}</tbody>
  </table>
</section>"""


def render_zoom(m, ctx):
    s = m.get("slots", {})
    base = to_uri(subst(s.get("base", ""), ctx), ctx["__base__"])
    calls = subst(s.get("callouts", []), ctx)
    tags = "".join(
        f'<div class="zoom-callout" style="left:{c.get("x",50)}%;top:{c.get("y",50)}%">{esc(c.get("label",""))}</div>'
        for c in calls if isinstance(c, dict)
    )
    return f"""<section class="mod mod-zoom" data-mod="detail_zoom">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  <div class="zoom-wrap"><img class="zoom-base" src="{esc(base)}">{tags}</div>
</section>"""


def render_scene(m, ctx):
    s = m.get("slots", {})
    img = to_uri(subst(s.get("img", ""), ctx), ctx["__base__"])
    tags = subst(s.get("tags", []), ctx)
    taghtml = "".join(f'<span class="badge">{esc(t)}</span>' for t in tags)
    return f"""<section class="mod mod-scene" data-mod="scene_show">
  {sec_head(s.get('title',''), s.get('sub',''), ctx)}
  <img class="scene-img" src="{esc(img)}">
  <div class="scene-tags">{taghtml}</div>
</section>"""


def render_spec(m, ctx):
    s = m.get("slots", {})
    items = subst(s.get("items", []), ctx)
    lis = []
    for it in items:
        if isinstance(it, dict):
            lis.append(f'<li><span class="spec-k">{esc(it.get("k",""))}</span><span class="spec-v">{esc(it.get("v",""))}</span></li>')
    shots = subst(s.get("shots", []), ctx)
    shotshtml = "".join(
        f'<img src="{esc(to_uri(x, ctx["__base__"]))}">' for x in shots
    )
    return f"""<section class="mod mod-spec" data-mod="spec_list">
  {sec_head(s.get('title','产品规格'), s.get('sub',''), ctx)}
  <ul class="spec-ul">{''.join(lis)}</ul>
  <div class="spec-shots">{shotshtml}</div>
</section>"""


def render_steps(m, ctx):
    s = m.get("slots", {})
    items = subst(s.get("items", []), ctx)
    vertical = s.get("layout") == "vertical"
    cells = []
    for i, it in enumerate(items):
        if isinstance(it, str):
            it = {"text": it}
        img = to_uri(it.get("img", ""), ctx["__base__"])
        imgtag = f'<img src="{esc(img)}">' if img else ""
        cells.append(
            f'<div class="step"><div class="idx">{i+1}</div>{imgtag}'
            f'<p class="t-body">{esc(it.get("text",""))}</p></div>'
        )
    return f"""<section class="mod mod-steps" data-mod="usage_steps">
  {sec_head(s.get('title','使用方法'), s.get('sub',''), ctx)}
  <div class="steps{' col' if vertical else ''}">{''.join(cells)}</div>
</section>"""


def render_trust(m, ctx):
    s = m.get("slots", {})
    items = subst(s.get("badges", []), ctx)
    notes = subst(s.get("notes", []), ctx)
    tbs = "".join(
        f'<div class="tb"><div class="tb-ico">{esc(b.get("icon","✓") if isinstance(b,dict) else "✓")}</div>'
        f'<span class="t-caption">{esc(b.get("text","") if isinstance(b,dict) else b)}</span></div>'
        for b in items
    )
    noteshtml = "".join(f'<p class="t-caption">{esc(n)}</p>' for n in notes)
    return f"""<section class="mod mod-trust" data-mod="trust_footer">
  <div class="trust-badges">{tbs}</div>
  <div class="trust-notes">{noteshtml}</div>
</section>"""


RENDERERS = {
    "hero_identity": render_hero,
    "pain_point":    render_pain,
    "feature_grid":  render_fgrid,
    "feature_list":  render_flist,
    "param_table":   render_table,
    "proof_data":    render_proof,
    "compare":       render_compare,
    "detail_zoom":   render_zoom,
    "scene_show":    render_scene,
    "spec_list":     render_spec,
    "usage_steps":   render_steps,
    "trust_footer":  render_trust,
}


# ---------------------------------------------------------------- 主流程
def build(spec, content, platform, base_dir):
    warnings = []
    plat = PLATFORMS.get(platform, PLATFORMS["taobao"])
    scale = plat["w"] / BASE_W

    # 变量上下文
    ctx = {}
    for k, v in content.get("fields", {}).items():
        ctx[k] = v
    for k, v in content.get("images", {}).items():
        ctx[k] = v
    ctx["__base__"] = base_dir
    ctx["__scale__"] = scale

    css_vars = build_css_vars(spec, scale, plat["min_fs"], warnings)

    # 渲染模块
    override = content.get("modules_override", {})
    parts = []
    for m in spec.get("modules", []):
        mid = m.get("id", "")
        ov = override.get(mid, {})
        if ov.get("enabled") is False:
            continue
        merged = dict(m)
        if "slots" in ov:
            merged_slots = dict(m.get("slots", {}))
            merged_slots.update(ov["slots"])
            merged["slots"] = merged_slots
        for k in ("items",):
            if k in ov:
                merged.setdefault("slots", {})[k] = ov[k]

        # 统一替换 {{变量}}，渲染函数拿到的都是终值
        merged["slots"] = subst(merged.get("slots", {}), ctx)

        mtype = merged.get("type", "custom")
        if merged.get("custom_html"):
            parts.append(subst(merged["custom_html"], ctx))
        elif mtype in RENDERERS:
            parts.append(RENDERERS[mtype](merged, ctx))
        else:
            warnings.append(f"[WARN] 未知模块类型 {mtype}（id={mid}），已跳过")

    body = "\n\n".join(parts)

    css = BASE_CSS.read_text(encoding="utf-8") if BASE_CSS.exists() else ""
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{esc(content.get('meta',{}).get('product_name','detail'))}</title>
<style>
{css}

/* ---- style-spec 注入 ---- */
:root {{
{css_vars}
}}
</style>
</head>
<body>
{body}
</body>
</html>"""
    return doc, warnings, plat


def main():
    ap = argparse.ArgumentParser(description="style-spec + content -> HTML")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--platform", default=None, help="覆盖 spec 里的平台设置")
    a = ap.parse_args()

    spec_p = Path(a.spec).resolve()
    content_p = Path(a.content).resolve()
    spec = load_json(spec_p)
    content = load_json(content_p)

    platform = a.platform or content.get("meta", {}).get("platform") or spec.get("meta", {}).get("platform") or "taobao"
    if platform not in PLATFORMS:
        print(f"[ERR] 未知平台 {platform}，可选: {', '.join(PLATFORMS)}")
        sys.exit(1)

    doc, warnings, plat = build(spec, content, platform, content_p.parent)

    out_p = Path(a.out).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(doc, encoding="utf-8")

    print(f"[OK] 已生成 {out_p}")
    print(f"     平台={platform} 画布宽={plat['w']}px 单图高上限={plat['max_h']}px 最小字号={plat['min_fs']}px")
    for w in warnings:
        print("     " + w)


if __name__ == "__main__":
    main()
