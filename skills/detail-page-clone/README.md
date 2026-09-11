# detail-page-clone · 详情图版式克隆与产品替换

> 给一张参考详情图，把它的版式骨架提取出来变成可复用模具；
> 之后只需要给产品图和产品信息，就能 1:1 出同版式的完整详情图。

---

## 适用场景

- "照着这张详情图做一套我们自己的"
- "详情图风格统一"——同一套版式，套不同产品
- "竞品详情图拆解复刻"——只学版式，不抄品牌
- 出图前自检（尺寸、字号下限、违禁词、占位符、竞品词残留）

---

## 两种用法

### 用法一：建新项目（推荐）

```bash
# 1) 新建项目目录
python scripts/init_project.py --name A35维它米 --platform taobao --root D:/电商图项目

# 2) 把参考详情图放进 {项目}/refs/
#    把自家产品图放进 {项目}/assets/
#    让 AI 读参考图，按 references/extraction-schema.md 填 style-spec.json
#    填 content.json（产品信息 + 图片路径）

# 3) 出图
cd {项目}
python .../scripts/build.py    --spec style-spec.json --content content.json --out build/index.html
python .../scripts/render.py   --html build/index.html --platform taobao --spec style-spec.json --out out/ --slice
python .../scripts/qa_check.py --spec style-spec.json --content content.json --html build/index.html --dir out/ --brands "竞品A 竞品B"
```

### 用法二：复用已有版式

如果已有别项目沉淀下来的 `style-spec.json`，新建项目时直接复用：

```bash
python scripts/init_project.py --name A35红虫 --platform pdd --root D:/电商图项目 --from-spec D:/老项目/style-spec.json
```

只换 `content.json` 里的图片路径、产品名、卖点、参数，就出图。

---

## 命令速查

| 命令 | 作用 |
|---|---|
| `init_project.py` | 建项目目录、复制模板 |
| `build.py` | style-spec + content → 自包含 HTML（CSS 变量驱动） |
| `render.py` | HTML → 整页长图 + 按平台切图 |
| `qa_check.py` | 出图前/后自检 |

### 常用参数

```bash
python render.py \
  --html build/index.html \
  --platform taobao \         # taobao | pdd | douyin | kuaishou | jd
  --spec style-spec.json \    # 按模块 id 命名切图
  --out out/ \
  --slice \                   # 按平台上限切图（默认按 --platform 自动）
  --format jpg --quality 90   # 默认 png；上架用 jpg
  --browser "C:/path/to/chrome.exe"  # 自动探测本机 Edge/Chrome，失败时可手动指定

python qa_check.py \
  --spec style-spec.json \
  --content content.json \
  --html build/index.html \
  --dir out/ \
  --platform taobao \
  --brands "老鬼 龙王恨 钓鱼王"   # 竞品品牌词，逗号或空格分隔
```

---

## 工作流（AI 执行手册）

### MODE A 学图（参考图 → 版式骨架）

1. **逐屏编号**：读参考图，按视觉分屏，每屏给一个 `id` 和 `type`
2. **拆四维度**：配色、字阶、版式骨架、装饰语法
3. **区分可迁移与禁迁移**：参考 [references/compliance-redlines.md](references/compliance-redlines.md)
4. **写 style-spec.json**：按 [references/extraction-schema.md](references/extraction-schema.md) 字段定义
5. **预览自查**：生成 `preview.html` 缩略图，肉眼与参考图对比

### MODE B 出图（产品图 → 成品）

1. 写 `content.json`（**只填有来源的事实**，不编参数、不编检测数据）
2. `build.py` → `render.py` → `qa_check.py`
3. 交付：`out/` 里的切图 + `build/index.html`（可浏览器打开直接看大图）
4. 把 `qa_check.py` 报出的 `open_questions` 一并交给用户确认

---

## 关键文件

```
detail-page-clone/
├── SKILL.md                          主入口，两模式说明
├── references/
│   ├── extraction-schema.md          style-spec.json / content.json 字段定义
│   ├── layout-atoms.md               版式原子库（每种模块的 HTML 结构）
│   ├── compliance-redlines.md        竞品图合规红线
│   └── platform-presets.md           各平台尺寸/字号下限
├── assets/
│   └── base.css                      CSS 变量驱动的样式基座
├── scripts/
│   ├── init_project.py               建项目
│   ├── build.py                      spec + content → HTML
│   ├── render.py                     HTML → 图（Edge/Chrome headless + Pillow 切图）
│   └── qa_check.py                   出图自检
└── examples/
    ├── default-spec.json             默认版式骨架（暖橙爆款）
    └── default-content.json          默认内容模板
```

---

## 输出规范

- **画布宽**：taobao/pdd 750px，douyin/kuaishou 1080px，jd 990px
- **单图高上限**：taobao 2000 / pdd 2500 / douyin 1920
- **最小字号**：taobao 24 / pdd 28 / douyin 32（render.py 自动抬升）
- **输出格式**：默认 PNG（无损）；上架建议 JPG 质量 90
- **命名规则**：`{序号}_{模块id}.jpg`，如 `03_feature_grid.jpg`

---

## 已知约束

1. 截图窗口硬上限 16000px（Chrome headless 限制）。超过需拆段渲染。
2. 大字号满屏（如 hero_title 144px × 7 行）会撑高页面，导致切图变多。
3. 复杂手绘装饰（路径、图形）不支持自动生成，需走 `custom_html` 字段手写。
4. 抠图、智能背景替换、AI 场景图需配合专用生图技能，本技能只负责精准排版与产品贴入。