#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_project.py — 新建一个详情图克隆项目目录。

用法:
  python init_project.py --name A35维它米 --platform taobao --root D:/电商图项目
  python init_project.py --name A35维它米 --from-spec D:/old/style-spec.json

产出结构:
  {root}/{name}/
    style-spec.json     版式骨架（从 examples 模板复制，或 --from-spec 复用已有）
    content.json        产品内容（待填）
    refs/               放参考图
    assets/             放产品图
    build/              中间 HTML
    out/                成品图
    QA.md               自检记录 + 待确认清单
"""
import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EXAMPLES = SKILL_DIR / "examples"

PLATFORM_LABEL = {
    "taobao": "淘宝/天猫", "pdd": "拼多多", "douyin": "抖音",
    "kuaishou": "快手", "jd": "京东",
}


def main():
    ap = argparse.ArgumentParser(description="新建详情图克隆项目")
    ap.add_argument("--name", required=True, help="项目名，如 A35维它米")
    ap.add_argument("--root", default=".", help="项目根目录")
    ap.add_argument("--platform", default="taobao",
                    choices=list(PLATFORM_LABEL))
    ap.add_argument("--from-spec", default=None, help="复用已有 style-spec.json")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    proj = root / a.name
    if proj.exists():
        print(f"[ERR] 目录已存在：{proj}")
        sys.exit(1)

    for sub in ("refs", "assets", "build", "out"):
        (proj / sub).mkdir(parents=True, exist_ok=True)

    # style-spec.json
    spec_dst = proj / "style-spec.json"
    if a.from_spec:
        shutil.copy(Path(a.from_spec).resolve(), spec_dst)
        spec = json.loads(spec_dst.read_text(encoding="utf-8"))
        spec.setdefault("meta", {})["platform"] = a.platform
        spec["meta"]["spec_id"] = f"{a.name}-{a.platform}-v1"
        spec_dst.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] 复用版式骨架 -> {spec_dst.name}")
    else:
        src = EXAMPLES / "default-spec.json"
        shutil.copy(src, spec_dst)
        spec = json.loads(spec_dst.read_text(encoding="utf-8"))
        spec["meta"]["platform"] = a.platform
        spec["meta"]["spec_id"] = f"{a.name}-{a.platform}-v1"
        spec["meta"]["spec_name"] = a.name
        spec["meta"]["created"] = date.today().isoformat()
        spec_dst.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] 已生成版式骨架模板 -> {spec_dst.name}（MODE A 学图后填写）")

    # content.json
    content_dst = proj / "content.json"
    shutil.copy(EXAMPLES / "default-content.json", content_dst)
    content = json.loads(content_dst.read_text(encoding="utf-8"))
    content["meta"]["platform"] = a.platform
    content["meta"]["product_name"] = a.name
    content["meta"]["spec_id"] = spec["meta"]["spec_id"]
    content_dst.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 已生成产品内容模板 -> {content_dst.name}")

    # QA.md
    qa = f"""# {a.name} — 详情图 QA 记录

- 平台：{PLATFORM_LABEL[a.platform]}（{a.platform}）
- 版式骨架：style-spec.json（spec_id = {spec['meta']['spec_id']}）
- 建项日期：{date.today().isoformat()}

## 流程记录

- [ ] MODE A 学图：参考图放入 refs/，拆解后填写 style-spec.json
- [ ] MODE B 出图：产品图放入 assets/，填写 content.json
- [ ] build.py 生成 HTML
- [ ] render.py 出图切图
- [ ] qa_check.py 自检通过
- [ ] 人工过一遍（缩略图看整体、原图看细节）

## 命令备忘

```bash
python build.py    --spec style-spec.json --content content.json --out build/index.html
python render.py   --html build/index.html --platform {a.platform} --out out/ --slice
python qa_check.py --spec style-spec.json --content content.json --html build/index.html --dir out/ --brands "竞品品牌词"
```

## 待确认清单

（把 qa_check 报出的 open_questions 抄到这里，逐项找用户确认）

"""
    (proj / "QA.md").write_text(qa, encoding="utf-8")
    print(f"[OK] 已生成 QA.md")

    print()
    print(f"项目已创建：{proj}")
    print("下一步：")
    if not a.from_spec:
        print("  1) 把参考详情图放进 refs/")
        print("  2) 让 AI 进入 MODE A：读取参考图 -> 填写 style-spec.json")
    print("  3) 把产品图放进 assets/，填写 content.json")
    print("  4) 跑 build -> render -> qa_check")


if __name__ == "__main__":
    main()
