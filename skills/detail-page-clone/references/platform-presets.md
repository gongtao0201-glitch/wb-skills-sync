# 平台尺寸预设

切换平台只改 `meta.platform`，`render.py` 自动套用下表参数。

| 平台 | platform 值 | 画布宽 | 单图高上限 | 最小字号 | 单图体积 | 说明 |
|---|---|---|---|---|---|---|
| 淘宝/天猫 | `taobao` | 750 | 2000 | 24 | ≤3MB | 主流标准，图片会被压缩，文字需加粗 |
| 拼多多 | `pdd` | 750 | 2500 | 28 | ≤2MB | 压缩最狠，字号要比淘宝再大一号 |
| 抖音 | `douyin` | 1080 | 1920 | 32 | ≤5MB | 竖版优先，小屏浏览，字必须大 |
| 京东 | `jd` | 990 | 2000 | 24 | ≤3MB | 白底偏好，装饰不宜过重 |
| 快手 | `kuaishou` | 1080 | 1920 | 32 | ≤5MB | 同抖音 |

## 缩放规则

`style-spec.json` 里的所有 px 值以 **750px 宽**为基准。切到 1080 时：

```
实际值 = round(基准值 × 目标宽 / 750)
```

例：主标题 72px @750 → 104px @1080。

## 字号下限

缩放后仍低于平台最小字号的，抬到下限值，并记入 QA 报告的 `warnings`：

```text
[WARN] hero_sub 由 22px 抬升至 28px（pdd 下限）
```

原因：电商图在手机上会被缩放显示，低于下限的字会糊成一团。

## 切图规则

整页截图后按以下逻辑切分，避免把文字拦腰截断：

1. **优先在模块边界切**（`modules[].id` 交界处）
2. 单模块高度超过上限时，在该模块内部寻找连续 ≥40px 的空白行切
3. 找不到安全点时，退化为等分切，并在 QA 报告里标记 `risk_cut`

```bash
python scripts/render.py --html build/index.html --platform pdd --out out/ --slice
```

输出：`out/01-hero.png`、`out/02-feature_grid.png` …，命名取自模块 id。

## 输出格式

| 场景 | 格式 | 说明 |
|---|---|---|
| 上架用 | JPG 质量 90 | 体积小，平台友好 |
| 需透明/二次编辑 | PNG | 体积大，仅中间产物 |
| 给美工 | PSD（配合 layered-psd-builder 技能） | 分层可改 |

```bash
python scripts/render.py --html build/index.html --format jpg --quality 90
```
