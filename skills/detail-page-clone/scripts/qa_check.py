#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_check.py — 出图前自检。跑在 build 之后、交付之前。

检查项:
  1. 画布宽 / 单图高 / 单图体积 是否符合平台规范
  2. 字阶是否低于平台最小字号
  3. HTML 里是否有未替换的 {{占位符}}
  4. content 引用的图片是否都存在
  5. 是否残留竞品品牌词（--brands 指定，空格分隔）
  6. 广告法违禁词扫描
  7. style-spec 与 content 的 spec_id 是否一致

用法:
  python qa_check.py --spec style-spec.json --content content.json --html build/index.html --dir out/ --platform taobao
  python qa_check.py --spec style-spec.json --content content.json --html build/index.html --brands "竞品A 竞品B"

退出码: 0 = 通过（可能有警告） / 1 = 有 ERROR
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLATFORMS = {
    "taobao":    {"w": 750,  "max_h": 2000, "min_fs": 24, "max_mb": 3},
    "pdd":       {"w": 750,  "max_h": 2500, "min_fs": 28, "max_mb": 2},
    "douyin":    {"w": 1080, "max_h": 1920, "min_fs": 32, "max_mb": 5},
    "kuaishou":  {"w": 1080, "max_h": 1920, "min_fs": 32, "max_mb": 5},
    "jd":        {"w": 990,  "max_h": 2000, "min_fs": 24, "max_mb": 3},
}

BANNED_WORDS = [
    # 极限词
    "最好", "最佳", "最强", "最优", "最高级", "最低价", "第一品牌", "全网第一", "排名第一",
    "国家级", "世界级", "顶级", "极致", "终极", "绝无仅有", "史无前例", "冠军", "领导者",
    "首创", "独一无二", "独家首创", "销量第一", "口碑第一",
    # 虚假承诺
    "根治", "永久", "100%有效", "包治", "无副作用", "零风险", "绝对", " guaranteed",
    # 贬损对比
    "秒杀", "碾压", "完爆", "吊打", "垃圾货",
    # 医疗功效
    "治疗", "疗效", "抗癌", "降压", "消炎", "壮阳", "治愈",
]

VAR_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_.\-]+)\s*\}\}")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def err(self, m):
        self.errors.append(f"[ERROR] {m}")

    def warn(self, m):
        self.warnings.append(f"[WARN ] {m}")

    def info(self, m):
        self.infos.append(f"[INFO ] {m}")

    def dump(self):
        for x in self.errors:
            print(x)
        for x in self.warnings:
            print(x)
        for x in self.infos:
            print(x)
        print("-" * 60)
        print(f"ERROR {len(self.errors)}  WARN {len(self.warnings)}  INFO {len(self.infos)}")
        return 1 if self.errors else 0


def main():
    ap = argparse.ArgumentParser(description="详情图出图前自检")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--html", default=None)
    ap.add_argument("--dir", default=None, help="成品图目录")
    ap.add_argument("--platform", default=None)
    ap.add_argument("--brands", default="", help="竞品品牌词，空格分隔")
    a = ap.parse_args()

    rep = Report()
    spec_p = Path(a.spec).resolve()
    content_p = Path(a.content).resolve()
    spec = json.loads(spec_p.read_text(encoding="utf-8"))
    content = json.loads(content_p.read_text(encoding="utf-8"))

    platform = a.platform or content.get("meta", {}).get("platform") \
        or spec.get("meta", {}).get("platform") or "taobao"
    plat = PLATFORMS.get(platform, PLATFORMS["taobao"])
    scale = plat["w"] / 750
    rep.info(f"平台={platform} 画布宽={plat['w']} 单图高上限={plat['max_h']} 最小字号={plat['min_fs']} 单图体积上限={plat['max_mb']}MB")

    # 1. spec_id 一致性
    sid_s = spec.get("meta", {}).get("spec_id")
    sid_c = content.get("meta", {}).get("spec_id")
    if sid_s and sid_c and sid_s != sid_c:
        rep.err(f"spec_id 不一致：style-spec={sid_s} / content={sid_c}")
    elif not sid_c:
        rep.warn("content.meta.spec_id 未填写，无法校验版式与内容是否配套")

    # 2. 字阶下限
    for item in spec.get("typography", {}).get("scale", []):
        fs = item.get("size_px")
        role = item.get("role", "?")
        if fs is None:
            rep.warn(f"字阶 {role} 缺少 size_px")
            continue
        scaled = round(float(fs) * scale)
        if scaled < plat["min_fs"]:
            rep.warn(f"字阶 {role} 缩放后 {scaled}px 低于平台下限 {plat['min_fs']}px，render 时会被抬升（可能导致换行）")

    # 3. 占位符残留
    if a.html and Path(a.html).exists():
        doc = Path(a.html).read_text(encoding="utf-8")
        found = sorted(set(VAR_RE.findall(doc)))
        if found:
            rep.err(f"HTML 残留未替换占位符 {len(found)} 个：{', '.join(found[:15])}")
            rep.info("检查 content.json 的 fields / images 是否补齐")
        else:
            rep.info("占位符全部替换完成")
    else:
        rep.warn("未提供 --html，跳过占位符检查")

    # 4. 图片存在性
    base = content_p.parent
    missing = []
    for k, v in (content.get("images") or {}).items():
        if not v:
            missing.append(f"{k}（空）")
            continue
        if re.match(r"^(https?:|data:)", v):
            continue
        if not (base / v).exists() and not Path(v).exists():
            missing.append(f"{k} -> {v}")
    if missing:
        rep.err(f"图片缺失 {len(missing)} 项：{', '.join(missing)}")
    else:
        rep.info("图片路径全部有效")

    # 5. 竞品品牌词残留
    brands = [b for b in a.brands.split() if b]
    if brands:
        hay = json.dumps(content, ensure_ascii=False)
        if a.html and Path(a.html).exists():
            hay += Path(a.html).read_text(encoding="utf-8")
        hit = [b for b in brands if b in hay]
        if hit:
            rep.err(f"检测到竞品品牌词残留：{', '.join(hit)}")
        else:
            rep.info(f"竞品品牌词检查通过（已扫描 {len(brands)} 个词）")
    else:
        rep.warn("未指定 --brands，跳过竞品品牌词检查（参考图为竞品时强烈建议指定）")

    # 6. 违禁词扫描
    hay = json.dumps(content, ensure_ascii=False)
    hits = [w for w in BANNED_WORDS if w in hay]
    if hits:
        rep.err(f"广告法违禁词命中：{', '.join(hits)}")
    else:
        rep.info("广告法违禁词扫描通过")

    # 7. 成品图检查
    if a.dir and Path(a.dir).exists():
        d = Path(a.dir)
        imgs = [p for p in d.iterdir()
                if p.suffix.lower() in (".png", ".jpg", ".jpeg")
                and not p.name.startswith(("00_", "_"))]
        if not imgs:
            rep.warn("成品目录里没有找到切图产物")
        for p in sorted(imgs):
            mb = p.stat().st_size / 1024 / 1024
            if mb > plat["max_mb"]:
                rep.warn(f"{p.name} 体积 {mb:.2f}MB 超过平台上限 {plat['max_mb']}MB")
            try:
                from PIL import Image
                with Image.open(p) as im:
                    w, h = im.size
                    if w != plat["w"]:
                        rep.err(f"{p.name} 宽度 {w}px ≠ 平台要求 {plat['w']}px")
                    if h > plat["max_h"]:
                        rep.err(f"{p.name} 高度 {h}px 超过上限 {plat['max_h']}px")
                    if h < 200:
                        rep.warn(f"{p.name} 高度仅 {h}px，可能是空段")
            except ImportError:
                rep.info("Pillow 未安装，跳过图片尺寸检查")
                break
        rep.info(f"成品图 {len(imgs)} 张已检查")

    # 8. open_questions
    oq = content.get("open_questions") or []
    if oq:
        rep.warn(f"content.open_questions 有 {len(oq)} 项待确认，交付时须一并交给用户：")
        for q in oq:
            rep.info("  - " + str(q))

    return rep.dump()


if __name__ == "__main__":
    sys.exit(main())
