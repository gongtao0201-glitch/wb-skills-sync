---
name: detail-page-clone
description: 从参考电商详情图提取可复用版式骨架（style-spec.json），再用用户自有产品图与产品信息 1:1 复刻出同版式详情图，支持淘宝/天猫、抖音、拼多多、京东多平台尺寸切换。用于"照着这张详情图做一套我们自己的""版式克隆""详情图换产品""竞品详情图拆解复刻""详情页统一风格"等需求。
---

# 详情图版式克隆（Detail Page Clone）

把一张参考详情图**变成一套可反复套用的版式模具**，之后只需要给产品图和产品信息，就能出同版式的完整详情图。

**核心原则：克隆版式，不克隆品牌。** 版式骨架、信息层级、配色逻辑、装饰语法是可以迁移的；品牌名、Logo、广告语、独有插画、产品摄影、数据结论是别人的版权资产，必须替换。

## 两种模式

先判断用户处在哪个模式：

| 信号 | 模式 |
|---|---|
| 用户给了参考图，说"学一下""照这个做""提取排版" | **MODE A 学图** |
| 已有 `style-spec.json`，用户给了产品图/产品信息，说"出图""套一下""换成我们的产品" | **MODE B 出图** |
| 用户只说"做详情图"，没给参考图 | 先问：有没有要对齐的参考图？没有就走 MODE B 并用 `examples/default-spec.json` 起手 |

---

## MODE A：学图（参考图 → 版式骨架）

输入：参考详情图（1 张长图，或 N 张分段图）+ 目标平台。

### A1. 逐屏编号，建立证据表

用 Read 工具逐张读取参考图，按视觉分屏切成"模块"，给每个模块编号并记录：

```
| 编号 | 类型 | 高度(px) | 构图 | 主文案 | 产品图位置/占比 | 装饰 |
|---|---|---|---|---|---|---|
| 01 | hero_identity | 1000 | 满版背景+中心产品 | 大字标题+3卖点 | 居中，占画面55% | 底部渐变 |
```

**必须记录像素级数据**：量出画布宽、每屏高、主标题字号（px）、色值（用取色得出 Hex）、模块间距。不确定的标 `?`，不要编。

### A2. 拆成四个维度

1. **配色系统** — 主色/辅色/强调色/背景/文字三级/分隔线，各给 Hex，并记录面积占比。
2. **字阶系统** — 按"角色"记录，不记字体名（字体名通常拿不到，记**字重+字号比+字距+对齐+颜色**）：
   `hero_title / section_title / point_title / body / caption / number / badge_text`
3. **版式骨架** — 每屏的构图模板、内容槽位（slot）坐标与占比。
4. **装饰语法** — 徽章、角标、分割线、标题两侧的翼形装饰、序号数字、纹理、渐变方向、阴影/倒影。

### A3. 区分「可迁移」与「禁迁移」

对照 [references/compliance-redlines.md](references/compliance-redlines.md) 逐项判定。**参考图是竞品图时，以下一律禁迁移**：品牌名、Logo、Slogan、代言/模特形象、独有插画与 IP 形象、产品实拍照片、具体检测数据与销量数字、专利号与认证标识、原创文案句式（长句照搬有风险，句式结构可用）。

### A4. 产出 style-spec.json

按 [references/extraction-schema.md](references/extraction-schema.md) 的字段定义写出 `style-spec.json`。这是整个技能的**唯一真相源**，后续出图全靠它。

模板骨架的生成方式：
- 默认用 `assets/base.css` 作为样式基座（CSS 变量驱动，改值即换风格）
- 若参考图版式高度定制化，在 `modules[].custom_html` 字段写入该模块的专属 HTML 片段

### A5. 产出骨架 HTML 并自查

生成 `preview.html`（用 spec 里的示例文案渲染），**必须自己看一遍**，确认：
- 模块顺序与参考图一致
- 字阶层级与参考图视觉比例接近
- 配色面积感接近
- 没有残留任何竞品品牌词

---

## MODE B：出图（产品图 → 成品详情图）

输入：`style-spec.json` + 产品图 + 产品信息（名称/卖点/参数/场景/资质）。

### B1. 收集产品事实，写 content.json

按 [references/extraction-schema.md](references/extraction-schema.md) 的 content 部分写。**只写用户提供的或能从产品图直接确认的事实**，不编参数、不编检测数据、不编销量。缺什么就在 `open_questions` 里列出来问用户，不要自己填空。

### B2. 套版式

```bash
python scripts/build.py --spec style-spec.json --content content.json --out build/index.html
```

`build.py` 会把 spec 的变量注入 CSS、按 `modules[]` 顺序渲染每个模块、把 content 的值填进槽位。

### B3. 渲染出图

```bash
python scripts/render.py --html build/index.html --platform taobao --out out/ --slice
```

自动探测本机 Edge/Chrome，headless 整页截图，再按模块边界安全切图（不切断文字），每张高度不超过平台上限。

### B4. QA 自检

```bash
python scripts/qa_check.py --spec style-spec.json --content content.json --dir out/
```

检查项：尺寸合规、最小字号达标、占位符残留、竞品品牌词残留、图片缺失、单图体积超标。

### B5. 交付

把成品图 + `preview.html` 一起给用户，并明确列出**待用户确认的项**（缺失素材、需核实的数据、需替换的占位文案）。

---

## 关键约束

1. **不编数据。** 参数、检测值、销量、成分含量必须有来源，没有就留空并标注。
2. **不抄文案。** 句式结构和信息层级可学，具体句子自己写。
3. **不换平台不改字阶下限。** 抖音字号最小 32px、拼多多 28px、淘宝 24px，低于此值在小屏上糊掉。切换平台时 `render.py` 会自动校验。
4. **产品图保真优先。** 用户给的是实拍图就直接用，不做形变、不换角度、不改包装颜色。需要抠图时明确告知，不做无声处理。
5. **每次出图都要能追溯到 spec。** 用户说"这块再大一点"，改的是 `style-spec.json`，不是直接改 HTML，否则下次套版式会丢。

## 参考文件

- [references/extraction-schema.md](references/extraction-schema.md) — style-spec.json / content.json 字段定义
- [references/layout-atoms.md](references/layout-atoms.md) — 版式原子库，每种模块类型的 HTML 结构与可调参数
- [references/compliance-redlines.md](references/compliance-redlines.md) — 竞品图合规红线与替换策略
- [references/platform-presets.md](references/platform-presets.md) — 各平台尺寸、切图上限、字号下限
- [scripts/init_project.py](scripts/init_project.py) — 新建项目目录
