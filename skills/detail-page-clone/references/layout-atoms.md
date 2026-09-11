# 版式原子库

每个模块类型对应一段 HTML 结构 + 一组可调参数。所有尺寸以 `canvas_width=750px` 为基准，写 spec 时直接给 px 值。

`build.py` 按 `modules[].type` 选模板，用 `slots` 的值填内容。通用 CSS 类在 `assets/base.css`。

---

## hero_identity — 首屏定位

**用途**：回答"这是什么、给谁、解决什么"。全页最重要，占屏通常 900–1200px。

**结构**
```html
<section class="mod mod-hero" style="--h:1000px; background:var(--c-bg-alt)">
  <div class="hero-top">
    <h1 class="t-hero_title">{{title}}</h1>
    <p  class="t-hero_sub">{{sub}}</p>
  </div>
  <div class="hero-visual">
    <img class="hero-product" src="{{product.src}}" style="--scale:55%">
  </div>
  <ul class="hero-points">
    <li class="badge">{{points.items[0]}}</li>
    <li class="badge">{{points.items[1]}}</li>
    <li class="badge">{{points.items[2]}}</li>
  </ul>
</section>
```

**可调参数**：`height_px`、`bg`、`title` 字号、`product.scale_pct`（产品占画面高度比）、`points` 数量（2–4）、产品是否有阴影/倒影。

**常见变体**
- `centered_product` — 产品居中，标题在上（最通用）
- `left_copy_right_product` — 左文案右产品，适合文案长的
- `full_bleed_scene` — 满版实景背景 + 产品贴入，适合场景型

---

## pain_point — 痛点共鸣

**用途**：让目标用户"被说中"。通常 1–2 屏。

```html
<section class="mod mod-pain" style="--h:600px">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <div class="pain-grid">
    <div class="pain-item" data-index="1">
      <div class="pain-icon">{{icon or index_number}}</div>
      <p class="t-body">{{text}}</p>
    </div>
    <!-- 2–4 个 -->
  </div>
</section>
```

**文案句式**：短句 + 具体情境。例："打窝半小时，浮漂一动不动"。避免抽象形容词。

---

## feature_grid — 卖点网格

**用途**：一次性摆出核心卖点。2/3/4 宫格。

```html
<section class="mod mod-fgrid" style="--h:auto">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <div class="grid grid-{{cols}}">
    <div class="card">
      <div class="card-img"><img src="{{item.img}}"></div>
      <h3 class="t-point_title">{{item.title}}</h3>
      <p class="t-body">{{item.desc}}</p>
    </div>
  </div>
</section>
```

**参数**：`cols`（2/3/4）、`card.bg`、`card.radius_px`、图片比例（`1:1` / `4:3` / `3:4`）。

**排版纪律**：每格字数控制在 12 字标题 + 20 字描述，超了会挤。

---

## feature_list — 卖点列表（左图右文交替）

**用途**：每个卖点需要单独展开讲。比网格信息量大。

```html
<section class="mod mod-flist">
  <div class="row" data-flip="false">
    <div class="row-img"><img src="{{item.img}}"></div>
    <div class="row-txt">
      <div class="idx">{{i+1}}</div>
      <h3 class="t-point_title">{{item.title}}</h3>
      <p class="t-body">{{item.desc}}</p>
    </div>
  </div>
  <!-- data-flip 交替 true/false -->
</section>
```

**参数**：图占宽比（默认 46%）、是否交替左右、序号样式。

---

## param_table — 参数表格

**用途**：规格信息，需要快速扫读。

```html
<section class="mod mod-table">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <table class="pt">
    <tr><th>{{k}}</th><td>{{v}}</td></tr>
  </table>
</section>
```

**参数**：`th` 宽度（默认 30%）、斑马纹开关、边框样式。

**纪律**：参数必须真实。没拿到的写"待补充"，不要编。

---

## proof_data — 数据证据

**用途**：用数字建立信任。视觉上是最抓眼的模块。

```html
<section class="mod mod-proof" style="background:var(--c-accent)">
  <div class="proof-item">
    <div class="t-number">{{value}}</div>
    <div class="t-caption">{{unit}}</div>
    <p class="t-body">{{desc}}</p>
  </div>
</section>
```

**参数**：数字字号（通常 56–88px）、深色底还是浅色底、一行摆 2 个还是 3 个。

**合规**：数值必须有检测报告或可验证来源，否则换成非数据型表达（如"快速散炮"）。

---

## compare — 对比

**用途**：我们 vs 普通/竞品。

```html
<section class="mod mod-compare">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <table class="cmp">
    <tr><th class="cmp-dim">{{维度}}</th><th class="cmp-us">本品</th><th class="cmp-oth">普通款</th></tr>
    <tr><td>{{row.dim}}</td><td class="yes">{{row.us}}</td><td class="no">{{row.other}}</td></tr>
  </table>
</section>
```

**合规红线**：不得出现竞品品牌名；不得用"秒杀""碾压"等贬损表述；对比项必须可客观验证。

---

## detail_zoom — 细节特写

**用途**：展示工艺、材质、结构。

```html
<section class="mod mod-zoom">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <div class="zoom-wrap">
    <img class="zoom-base" src="{{base}}">
    <div class="zoom-callout" style="left:{{x}}%;top:{{y}}%">
      <span class="t-caption">{{label}}</span>
    </div>
  </div>
</section>
```

**参数**：主图、标注点位（百分比坐标）、引线样式。

---

## scene_show — 场景代入

**用途**：让用户看到自己使用的样子。

```html
<section class="mod mod-scene">
  <h2 class="t-section_title">{{title}}</h2>
  <img class="scene-img" src="{{img}}">
  <div class="scene-tags">
    <span class="badge">{{tag}}</span>
  </div>
</section>
```

**参数**：场景图是否满版、标签位置、是否加渐变遮罩提升文字可读性。

---

## spec_list — 规格清单

**用途**：回答"我会收到什么"，减少售后纠纷。

```html
<section class="mod mod-spec">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <ul class="spec-ul">
    <li><span class="spec-k">{{k}}</span><span class="spec-v">{{v}}</span></li>
  </ul>
  <div class="spec-shots"><img src="{{pack_img}}"></div>
</section>
```

**内容**：净含量、尺寸、SKU 选项、包装内含物、批次/保质期。

---

## usage_steps — 使用步骤

```html
<section class="mod mod-steps">
  <div class="sec-head"><h2 class="t-section_title">{{title}}</h2></div>
  <div class="steps">
    <div class="step">
      <div class="idx">{{i+1}}</div>
      <img src="{{step.img}}">
      <p class="t-body">{{step.text}}</p>
    </div>
  </div>
</section>
```

**参数**：横排还是竖排、步骤数（3–5）、是否带箭头连接。

---

## trust_footer — 信任收口

**用途**：资质、售后、注意事项。

```html
<section class="mod mod-trust" style="background:var(--c-bg-alt)">
  <div class="trust-badges">
    <div class="tb"><div class="tb-ico">{{icon}}</div><span class="t-caption">{{text}}</span></div>
  </div>
  <div class="trust-notes">
    <p class="t-caption">{{note}}</p>
  </div>
</section>
```

**内容**：正品保障、退换政策、发货时效、使用注意。**不得编造认证与资质**。

---

## custom — 自定义

spec 模块里写 `custom_html` 字段时，`build.py` 原样输出。用于参考图里有内置模板覆盖不了的版式。

```jsonc
{
  "id": "special",
  "type": "custom",
  "custom_html": "<section class='mod' style='--h:800px'>...</section>"
}
```

自定义片段里同样支持 `{{变量}}` 替换。

---

## 通用槽位变量约定

| 变量 | 含义 |
|---|---|
| `{{product_name}}` | 产品全名 |
| `{{core_promise}}` | 一句话核心承诺 |
| `{{img_main}}` / `{{img_scene}}` / `{{img_detail_N}}` | 图片路径，来自 content.images |
| `{{point_N}}` | 卖点短语 |
| `{{param.*}}` | 参数字段 |

未在 content.json 中找到值的变量，`qa_check.py` 会报"占位符残留"。
