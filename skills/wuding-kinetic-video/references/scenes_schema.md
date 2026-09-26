# 分镜脚本 schema（scenes.json）

顶层字段：

```json
{
  "skin": "tech",                 // tech=深墨+薄荷/天蓝/珊瑚（默认）| wuding=五鼎绿橙
  "badge": "五鼎源 × 老歌哥",      // 右上常驻角标
  "foot":  "底部常驻小字",          // 可写数据来源/口径声明
  "orient": "landscape",          // landscape=1920×1080（默认）| portrait=1080×1920
  "scenes": [ ... ]
}
```

每幕通用字段：`type` + `dur`（秒，必填）。

## 1. title / end（片头 / 片尾）
```json
{"type":"title","dur":4.5,
 "eyebrow":"KINETIC VIDEO",
 "brand":"五鼎动画工厂",
 "title":"一篇笔记，一条动画视频",
 "sub":"分镜 · 排版 · 动效 · 成片，一条指令跑完"}
```
`end` 额外支持：`tags":["调研笔记","口播稿","产品页"]","cta":"一句话开工"`。
动效：品牌字 elastic 弹入 → 标题逐字上滑（stagger 0.045）→ 副标淡入 → dashed ring 慢速旋转 → 片尾 CTA 弹入。

## 2. points（要点卡，2–4 张最佳）
```json
{"type":"points","dur":7,"head":"这套流水线能干什么",
 "items":[{"icon":"light","t":"知识讲解","d":"讲到一个观点，画面立刻把它讲清楚"}]}
```
icon 可选：`light / layers / bolt / chart / box / pen / gear / heart / check / play`
动效：卡片 elastic 弹入（stagger 0.14）+ 图标 SVG 描边生长。竖屏下卡片自动纵向堆叠。

## 3. bigword（大字强调）
```json
{"type":"bigword","dur":4,"eyebrow":"核心不是提示词","word":"分镜","note":"先拆幕，再定每幕的动作"}
```
动效：大字 elastic 放大 + 轻微回旋。

## 4. typewriter（打字机）
```json
{"type":"typewriter","dur":6.5,"head":"底层在做什么",
 "text":"把每一幕写进工程配置，GSAP 按时执行，浏览器一帧一帧画出来。",
 "note":"不是一句提示词，是写死的动作表"}
```
动效：文字逐字打出 + 光标闪烁 + 面板横向展开。

## 5. flow（流程 / 步骤，2–4 步）
```json
{"type":"flow","dur":6.5,"head":"三步落地",
 "steps":[{"t":"文稿","d":"一篇笔记或口播稿"},{"t":"分镜","d":"拆成 5–8 幕"},{"t":"成片","d":"1920×1080 · 30fps"}]}
```
动效：节点 back 弹入（stagger 0.22）+ 箭头描边生长。竖屏下箭头自动旋转 90°。

## 6. bars（数据条）
```json
{"type":"bars","dur":6,"head":"值不值得做",
 "items":[{"label":"重复利用率","v":90,"suffix":"%"},{"label":"单条耗时下降","v":75,"suffix":"%"}]}
```
动效：进度条生长（power3.out）+ 数字同步计数。
**铁律**：v 必须是真实或明确标注的估算值；非实测数据必须在 `foot` 里声明口径。

## 7. quote（金句）
```json
{"type":"quote","dur":5,"text":"你只管想清楚讲什么，画面交给代码。","by":"老歌哥 · 五鼎源"}
```
动效：引号弹入 + 正文逐字上滑 + 署名滑入。

## 8. free（自定义 HTML 幕）
```json
{"type":"free","dur":5,"html":"<div style='font-size:80px'>任意排版</div>"}
```

## 9. TTS 配音输入（script.json）

与 `scenes.json` 一一对应，每幕一句口播：

```json
{
  "voice": "zh-CN-YunyangNeural",
  "rate": "+0%",
  "lines": [
    "老歌哥新先说。退休之后，把日子过成诗。100种雅致玩法，说到底只讲了三个字。",
    "公园里常见的退休状态有两种。",
    "刷手机，一坐一下午，眼神是空的。",
    "真正的敌人不是没钱，而是被需要感。",
    "雅致不是花钱，是花心思。",
    "三个转变，把时间还给自己。",
    "退休后的自由，不是想做什么就做什么，而是想不做什么就不做什么。",
    "退休前，时间是别人的；退休后，时间主权回到自己手里。",
    "把时间还给自己。退休不是落幕，是人生真正自由的开始。"
  ]
}
```

运行 `tts_scenes.py script.json scenes.json <输出目录>` 后得到：
- `voice.mp3`：整轨配音
- `timing.json`：每幕音频时长
- `scenes_vo.json`：每幕 `dur = audio + 1s` 留白，可直接用于渲染

## 渲染参数（render.mjs）

```powershell
render.mjs <html> <framesDir> [--fps=30] [--scale=1] [--quality=92] [--start=N] [--end=N]
```

- `--start`/`--end`：按帧号范围分段并行，避免长后台被 kill
- `--quality`：JPEG 质量，80 可提速约 15–20%，画质损失不明显

## 时长建议
| 成片目标 | 幕数 | 单幕时长 |
|---|---|---|
| 30s 快闪 | 5–6 | 4–5s |
| 45s 标准讲解 | 7–8 | 4.5–7s |
| 60s 深度 | 9–11 | 5–6s |
| 60–80s 配音版 | 8–9 | 以 audio 时长 + 1s 留白为锚 |

口播配套：约 4 字/秒，45s 视频配 180 字左右口播稿。
