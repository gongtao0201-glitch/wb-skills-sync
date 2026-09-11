# style-spec.json 与 content.json 字段定义

## 一、style-spec.json（版式骨架，学图产物）

一份 spec = 一套版式模具。文件路径建议：`{项目}/style-spec.json`。

```jsonc
{
  "meta": {
    "spec_id": "a35-vitami-hero-v1",
    "spec_name": "A35维它米·暖橙爆款版式",
    "source_refs": ["refs/competitor_01.png", "refs/competitor_02.png"],
    "source_type": "competitor",            // competitor | own | stock
    "platform": "taobao",                   // taobao | douyin | pdd | jd
    "canvas_width": 750,
    "created": "2026-09-03",
    "notes": "参考图是竞品图，品牌资产已全部剔除，仅保留版式与配色逻辑"
  },

  "palette": {
    "primary":   "#E23A1A",   // 主色：标题、强调、按钮
    "secondary": "#F5A623",   // 辅色：色块、渐变、次要强调
    "accent":    "#1B1B1B",   // 深色：正文主色、深色背景
    "bg_base":   "#FFFFFF",   // 主背景
    "bg_alt":    "#FFF6EC",   // 交替背景（模块间隔用）
    "text_main": "#1B1B1B",
    "text_sub":  "#6B6B6B",
    "text_inverse": "#FFFFFF",
    "line":      "#EDEDED",
    "area_ratio": "主色15% / 辅色10% / 背景+留白65% / 深色10%"
  },

  "typography": {
    "font_stack": "'Microsoft YaHei','Noto Sans SC','PingFang SC',sans-serif",
    "title_font_stack": "'Microsoft YaHei','Noto Sans SC',sans-serif",
    "scale": [
      { "role": "hero_title",    "size_px": 72, "weight": 900, "color": "var(--c-accent)",  "letter_spacing": "0.02em", "align": "center", "line_height": 1.15 },
      { "role": "hero_sub",      "size_px": 32, "weight": 400, "color": "var(--c-text-sub)","letter_spacing": "0.08em", "align": "center", "line_height": 1.5 },
      { "role": "section_title", "size_px": 48, "weight": 800, "color": "var(--c-accent)",  "letter_spacing": "0.02em", "align": "center", "line_height": 1.25 },
      { "role": "section_sub",   "size_px": 24, "weight": 400, "color": "var(--c-text-sub)", "letter_spacing": "0.1em",  "align": "center", "line_height": 1.5 },
      { "role": "point_title",   "size_px": 34, "weight": 700, "color": "var(--c-primary)", "letter_spacing": "0",      "align": "left",   "line_height": 1.35 },
      { "role": "body",          "size_px": 26, "weight": 400, "color": "var(--c-text-main)","letter_spacing": "0.01em", "align": "left",   "line_height": 1.75 },
      { "role": "caption",       "size_px": 22, "weight": 400, "color": "var(--c-text-sub)", "letter_spacing": "0",      "align": "left",   "line_height": 1.5 },
      { "role": "number",        "size_px": 64, "weight": 900, "color": "var(--c-primary)",  "letter_spacing": "-0.02em","align": "center", "line_height": 1 },
      { "role": "badge_text",    "size_px": 22, "weight": 700, "color": "var(--c-text-inverse)", "letter_spacing": "0.05em", "align": "center", "line_height": 1 }
    ],
    "min_size_guard": true      // true 时 render.py 按平台下限强制抬升过小字号
  },

  "decor": {
    "badge":       { "shape": "rounded_rect", "radius_px": 8, "bg": "var(--c-primary)", "color": "var(--c-text-inverse)", "padding": "8px 20px" },
    "divider":     { "type": "dashed", "color": "var(--c-line)", "width_px": 1, "margin_px": 40 },
    "section_head":{ "style": "title_with_wings", "wing": "short_line", "wing_color": "var(--c-primary)", "gap_px": 24 },
    "index_number":{ "style": "filled_circle", "size_px": 56, "bg": "var(--c-primary)", "color": "var(--c-text-inverse)" },
    "card":        { "bg": "var(--c-bg-alt)", "radius_px": 12, "padding_px": 32, "shadow": "0 4px 16px rgba(0,0,0,.06)" },
    "texture":     "none",        // none | noise | paper | gradient
    "gradient":    { "from": "#FFF6EC", "to": "#FFFFFF", "deg": 180 },
    "product_shadow": "0 12px 32px rgba(0,0,0,.16)",
    "product_reflection": false
  },

  "modules": [
    {
      "id": "hero",
      "type": "hero_identity",
      "height_px": 1000,
      "bg": "var(--c-bg-alt)",
      "layout": "full_bleed_bg + centered_product",
      "composition_note": "背景满版，产品居中占画面高度55%，顶部大标题，底部三卖点横排",
      "slots": {
        "title":    { "role": "hero_title", "text": "{{product_name}}" },
        "sub":      { "role": "hero_sub",   "text": "{{core_promise}}" },
        "product":  { "src": "{{img_main}}", "scale_pct": 55, "align": "center", "offset_y_pct": 52 },
        "points":   { "role": "badge_text", "items": ["{{point_1}}", "{{point_2}}", "{{point_3}}"] }
      }
    }
  ],

  "copy_patterns": {
    "hero_title":    "{{product_name}}｜{{one_line_position}}",
    "point_head":    "{{number}}{{unit}} {{benefit}}",
    "proof_line":    "实测{{metric}}达{{value}}",
    "cta":           "{{action}}，{{result}}",
    "note":          "句式结构可学，具体词必须自己写，禁止照搬竞品原句"
  },

  "avoid": [
    "竞品品牌名、Logo、Slogan",
    "竞品独有的插画/IP/模特形象",
    "未经验证的检测数据与销量",
    "极限词：最、第一、顶级、国家级"
  ],

  "open_questions": []
}
```

### 模块 type 一览（HTML 结构见 layout-atoms.md）

| type | 用途 |
|---|---|
| `hero_identity` | 首屏定位：产品名 + 核心承诺 + 主图 |
| `pain_point` | 痛点共鸣：使用前情境 |
| `feature_grid` | 卖点网格：2/3/4 宫格图文 |
| `feature_list` | 卖点列表：左图右文交替 |
| `param_table` | 参数表格 |
| `proof_data` | 数据/证据：大数字 + 说明 |
| `compare` | 对比：我们 vs 普通 |
| `detail_zoom` | 细节特写：多图拼贴 + 标注 |
| `scene_show` | 场景代入：人群/时刻 |
| `spec_list` | 规格清单：尺寸、SKU、包装内容 |
| `usage_steps` | 使用步骤：1-2-3 |
| `trust_footer` | 信任收口：资质、售后、提醒 |
| `custom` | 自定义，用 `custom_html` 字段 |

### 字段说明

- **`size_px` 一律以 `canvas_width=750` 为基准**。切到其他平台时 `render.py` 按 `目标宽/750` 等比缩放，再套字号下限。
- `slots` 里的 `{{变量}}` 在 MODE B 由 `content.json` 的 `fields` 填充。
- `modules[].custom_html` 存在时，`build.py` 直接输出该片段，跳过内置模板。

---

## 二、content.json（产品内容，出图输入）

```jsonc
{
  "meta": {
    "spec_id": "a35-vitami-hero-v1",   // 必须与 style-spec.json 的 meta.spec_id 一致
    "platform": "taobao",
    "product_name": "西部风 A35 维它米"
  },

  "images": {
    "img_main":   "assets/a35-main.png",
    "img_scene":  "assets/a35-scene.jpg",
    "img_detail_1": "assets/a35-detail-1.jpg",
    "img_detail_2": "assets/a35-detail-2.jpg"
  },

  "fields": {
    "product_name": "西部风 A35 维它米",
    "core_promise": "一粒入水，30秒散炮成窝",
    "one_line_position": "酒米窝料·快速聚鱼",
    "point_1": "酒香发酵",
    "point_2": "30秒散炮",
    "point_3": "留鱼持久",
    "metric": "雾化时间",
    "value": "30秒"
  },

  "modules_override": {
    // 可选。用于开关模块或覆盖某模块内容，键 = style-spec 里的模块 id
    "compare":    { "enabled": false },
    "feature_grid": {
      "items": [
        { "title": "酒香发酵", "desc": "低温慢发酵 72 小时", "img": "assets/a35-detail-1.jpg" },
        { "title": "快速散炮", "desc": "入水 30 秒形成雾化带", "img": "assets/a35-detail-2.jpg" }
      ]
    }
  },

  "open_questions": [
    "缺少第三方检测报告，proof_data 模块的数值待用户提供",
    "礼盒装 SKU 清单未提供，spec_list 暂用单瓶规格"
  ]
}
```

### 填写规则

1. **只填有来源的事实。** 产品名、规格、成分来自包装或用户口述；检测值、销量、排名必须有凭证。
2. **图片路径相对 content.json 所在目录。** 缺失的图 `qa_check.py` 会报出来。
3. **`open_questions` 必填。** 缺什么写什么，出图后一并交给用户确认。
4. 极限词（`最`/`第一`/`顶级`/`国家级`/`根治`/`永久`）属于广告法违禁，`qa_check.py` 会拦截。
