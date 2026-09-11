---
name: canvas-design-product-poster
description: |
  Generate high-quality product launch posters using the canvas-design philosophy.
  Trigger when the user asks to create a poster with canvas-design, especially for product launches / new product announcements,
  or when they mention "3:2 poster", "新品发布海报", "产品海报", "上市海报" together with canvas-design.
  Reads product images/assets from a local folder, writes a design philosophy manifesto,
  and renders a polished PNG via Python/Pillow with a 3:2 aspect ratio.
description_zh: |
  基于 canvas-design 视觉哲学生成 3:2 产品新品发布海报。
  当用户要求用 canvas-design 出海报、产品上市海报、新品发布海报或 3:2 海报时触发。
  流程：读取本地产品素材 → 撰写 design-philosophy.md → 用 Python + Pillow 输出高品质 PNG。
version: "1.0.0"
license: "MIT"
allowed-tools: Read,Write,Bash
display_name: "Canvas Design 产品海报"
display_name_en: "Canvas Design Product Poster"
visibility: "private"
agent_created: true
---

# Canvas Design 产品海报生成器

## 触发场景
- 用户说"用 canvas-design 出一张...海报"
- 用户要求生成产品新品发布 / 上市 / 首发海报
- 用户指定 3:2 比例海报
- 用户提供包含产品图片的本地文件夹，要求据此生成海报

## 核心原则（来自 canvas-design）
1. **视觉优先**：信息通过色彩、构图、空间传达，文字仅作必要锚点。
2. **极简文字**：只保留品牌、产品名、型号、"新品发布"、核心卖点、口味/规格标签。
3. **专家级工艺**：排版精确对齐、留白充足、无任何元素重叠、配色克制且与产品包装一致。
4. **第二遍精修**：不新增图形，只 refinement 现有元素，让整体更 cohesive。

## 执行流程

### 1. 定位并读取素材
- 找到用户指定的文件夹（通常含产品包装图 / 实物图）。
- 用 `Read` 读取图片，提取：品牌名、产品名、型号、卖点文案、口味/规格、主视觉色。
- 若图片是透明背景 PNG，可直接融入海报。

### 2. 撰写设计哲学
- 在目标文件夹输出 `design-philosophy.md`。
- 命名一个 1-2 词的视觉运动（如 "Amber Tension"）。
- 写 4-6 段，涵盖：空间与形式、色彩与材质、尺度与节奏、构图与平衡、视觉层级。
- 反复强调「meticulously crafted」「master-level execution」「 painstaking attention」。

### 3. 生成海报（Python + Pillow）
- **画布尺寸**：1800 × 1200 px（3:2），RGB 输出。
- **依赖**：在隔离 venv 中安装 Pillow：`pip install pillow`。
- **字体**：
  - 中文：`C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf`（或 Microsoft YaHei）
  - 英文/数字：使用 `canvas-design/canvas-fonts` 下的 `BigShoulders-Bold.ttf`
- **配色**：取自产品包装主色，通常红/金/白/黑。
- **布局建议**：
  - 左侧 35-40% 放产品瓶身/实物图，带柔和阴影或光晕。
  - 右侧放文字区：品牌 → 产品名 → 型号 → 新品发布 → 核心卖点 → 口味标签。
  - 底部一条细金线，角落可放一句极简英文 craft mark（可选）。

### 4. 精修检查
- 文字是否重叠？
- 产品是否贴边？是否留出呼吸空间？
- 右侧是否太空或太挤？
- 装饰线条是否完整、克制？
- 保存前用 `Read` 预览确认。

## 输出文件
- `{产品名}_新品发布海报.png`（1800×1200，3:2）
- `design-philosophy.md`（生成所用的视觉哲学）

## 注意事项
- canvas-design 强调艺术性，但产品海报仍需保留商业必需信息；在「极简」和「可读」之间取平衡。
- 不要过度使用英文装饰句；若使用，保持与钓鱼/户外/产品气质相关或完全抽象。
- 如果用户没有指定中文字体，默认使用系统 Noto Sans SC，避免方块字。
