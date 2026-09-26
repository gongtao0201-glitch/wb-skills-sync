---
name: wuding-kinetic-video
display_name: "五鼎动画工厂"
display_name_en: "Wuding Kinetic Video"
description_zh: |
  五鼎动画工厂——把一篇笔记/文稿/产品介绍一句话变成动画视频（HTML+GSAP 分镜动画 → 无头浏览器逐帧渲染 → H.264 MP4）。当用户说「把这篇笔记做成动画视频」「做一个讲解动画」「知识动画」「产品介绍动画」「像 Hyperframes 那样的动画视频」「motion graphics 视频」时触发。四交付：自适应 HTML（带播放控制）、横屏 16:9 MP4、竖屏 9:16 MP4、TTS 配音版 MP4。
description_en: |
  五鼎动画工厂——把一篇笔记/文稿/产品介绍一句话变成动画视频（HTML+GSAP 分镜动画 → 无头浏览器逐帧渲染 → H.264 MP4）。当用户说「把这篇笔记做成动画视频」「做一个讲解动画」「知识动画」「产品介绍动画」「像 Hyperframes 那样的动画视频」「motion graphics 视频」时触发。四交付：自适应 HTML（带播放控制）、横屏 16:9 MP4、竖屏 9:16 MP4、TTS 配音版 MP4。
version: 1.0.0
agent_created: true
license: MIT
category: design
platforms:
- WorkBuddy
---

# 五鼎·动画工厂（Kinetic Video）

> **定位**：对标 Hyperframes 的自建动画视频流水线。核心思路——动画不靠一句提示词，而是把「分镜结构 + 每幕的具体动作」写进工程配置，由 GSAP 按时间轴执行，无头浏览器逐帧截图收成 MP4。
> 与既有技能分工：#45=数据榜单竖屏视频（Remotion）；#48=口播稿→3:4 竖屏 TTS 视频；**本技能=知识讲解/教程/产品介绍类动画视频，含 16:9 横屏、9:16 竖屏、TTS 配音版**。

## 🚀 一句话 SOP（接到指令即跑，默认值直接用）

1. **读稿拆幕**：读用户给的笔记/文稿，拆成 5–8 幕，写 `scenes.json`（schema 见 `references/scenes_schema.md`）。
2. **（可选）配音**：如需 TTS，写 `script.json`，运行 `scripts/tts_scenes.py script.json scenes.json <输出目录>` 生成 `voice.mp3` + `scenes_vo.json`（每幕 dur 按配音时长自动补齐）。
3. **构建 HTML**：
   ```powershell
   node C:\Users\HP\.workbuddy\skills\wuding-kinetic-video\scripts\build_html.mjs <scenes.json|scenes_vo.json> <输出目录>\<名>.html
   ```
4. **抽帧验证 / 程序化溢出检测**：
   ```powershell
   # 快速抽 8 张关键帧
   node ...\scripts\render.mjs <html> _preview --only=90,353,647,887,1150,1469,1717,1913,2151
   # 若无法看图，跑程序化溢出检测
   node ...\scripts\check_overflow.mjs <html>
   ```
5. **全量渲染**：单段后台或用 `--start`/`--end` 分段并行（见下）。
6. **编码 + 混音**：
   ```powershell
   node ...\scripts\encode.mjs _frames <名>-1920x1080-30fps.mp4
   ffmpeg -i <名>-1920x1080-30fps.mp4 -i voice.mp3 -c:v copy -c:a aac -b:a 192k -shortest <名>-配音版.mp4
   ```
7. **交付**：`present_files` 交 HTML + MP4（横屏/竖屏/配音版按需）；写当日 workspace 记忆。

**node 路径固定用**：`C:\Users\HP\.workbuddy\binaries\node\versions\22.22.2-2\node.exe`

## 默认决策（不问，直接用）

| 项 | 默认值 |
|---|---|
| 横屏规格 | 1920×1080（16:9）、30fps、H.264 MP4（-crf 20） |
| 竖屏规格 | 1080×1920（9:16）、30fps、H.264 MP4；scenes.json 顶层加 `"orient":"portrait"` |
| 时长 | 30–80s（8–9 幕 ≈ 44–76s） |
| 皮肤 | `tech`（深墨 #06121F + 薄荷 #2FE3C7 / 天蓝 #38BDF8 / 珊瑚 #F7A66A）；退休/生活方式主题换 `skin:"wuding"`（深墨绿底 + 温柔绿/怀旧橙） |
| 角标 | 「你的品牌 × 老歌哥」（badge 字段可改） |
| 结构 | 片头(title) → 要点(points) → 强调(bigword) → 深入(typewriter) → 流程(flow) → 数据(bars) → 金句(quote) → 片尾(end)，可裁剪组合 |
| 输出位置 | `09-0全域创业素材\<主题名>\` |

## 场景类型速查

| type | 用途 | 关键动效 |
|---|---|---|
| `title` / `end` | 片头片尾 | 品牌字 elastic 弹入、标题逐字上滑、dashed ring 旋转 |
| `points` | 2–4 张要点卡 | 卡片 elastic 弹入 + icon SVG 描边（横排，竖屏自动纵向堆叠） |
| `bigword` | 单个大字强调 | elastic 放大回旋 |
| `typewriter` | 一句核心解释 | 打字机 + 光标闪烁 |
| `flow` | 2–4 步流程 | 节点 back 弹入 + 箭头描边（竖屏箭头自动旋转 90°） |
| `bars` | 2–4 条数据 | 进度条生长 + 数字计数 |
| `quote` | 金句 | 引号弹入 + 逐字上滑 |
| `free` | 自定义 | 任意 HTML |

完整字段与示例 → `references/scenes_schema.md`

## 横屏长片分段并行渲染

超过 1500 帧或时长超过 60s 的片子，**不要**把「渲染+编码+混音」串成一条长后台命令，易被超时 kill。分两段/四段：

```powershell
# 4 段并行（每段 573 帧 ≈ 10 分钟）
render.mjs <html> _frames --start=0   --end=573
render.mjs <html> _frames --start=573 --end=1146
render.mjs <html> _frames --start=1146 --end=1719
render.mjs <html> _frames --start=1719 --end=2292
```

文件名为 `f#####.jpg`，各段范围不重叠，可直接合并编码。

## TTS 配音工作流

1. 准备 `script.json`：
   ```json
   {
     "voice": "zh-CN-YunyangNeural",
     "rate": "+0%",
     "lines": ["幕0口播", "幕1口播", "..."]
   }
   ```
2. 运行 `python scripts/tts_scenes.py script.json scenes.json <输出目录>`：
   - 逐幕生成 mp3 → 统一 pad/拼接成 `voice.mp3`
   - 输出 `scenes_vo.json`（每幕 `dur = audio + 1s 留白`）
3. 用 `scenes_vo.json` 构建 HTML，渲染无声 MP4，最后 ffmpeg 混音：
   ```powershell
   ffmpeg -y -i silent.mp4 -i voice.mp3 -c:v copy -c:a aac -b:a 192k -shortest voiced.mp4
   ```

## 程序化溢出检测

当无法/不便看图时：

```powershell
node ...\scripts\check_overflow.mjs <html>
```

脚本会 seek 到每幕中点，递归检测所有元素是否超出画布，输出 ✅/❌。

## 铁律

1. **逐帧确定性渲染**：渲染走 `window.__KINETIC__.seek(t)`（GSAP timeline pause+seek），不依赖真实播放速度——机器再慢也不会掉帧。
2. **先抽帧后全量**：全量渲染前必看 `_preview` 静帧或跑 `check_overflow`。
3. **不造伪数据**：bars 数值必须真实或明确标注估算；非实测数据写进 `foot` 声明。
4. **每幕内容包在 `.scene-inner`**（模板已固化）：进出场由外层统一管理，避免 GSAP seek 状态错乱（hard-kill 问题）。
5. **去AI味**：文案自然口语，禁「以上就是/综上所述」；正文不出现「第一幕/第二幕」这类骨架词。
6. **临时帧目录**（`_frames`/`_preview`，约 200MB）交付后可删，保留 HTML+MP4+scenes.json 即可复改。

## 环境依赖（已装好，无需重装）

- GSAP 3.12.5：`assets/gsap.min.js`（本地，构建时内联）
- Chromium：`C:\Users\HP\AppData\Local\ms-playwright\chromium-1234\chrome-win64\chrome.exe`（render.mjs 自动探测，也可 `--chrome=` 指定或用 Edge）
- playwright-core：`C:\Users\HP\.workbuddy\binaries\node\workspace\node_modules`
- ffmpeg（H.264）：`09-0全域创业素材\Tools\ffmpeg\ffmpeg.exe`（encode.mjs 自动探测；npm 备份在 workspace node_modules `@ffmpeg-installer`）
- edge-tts：Python venv `C:\Users\HP\.workbuddy\binaries\python\envs\default\Scripts\python.exe` 已装，用于 TTS。
- ⚠️ Playwright 自带 `ffmpeg-win64.exe` 是精简版（只有 VP8/webm），**不能**出 H.264 MP4，别用错。

## 常见坑

- **字体**：Windows 无 PingFang SC，模板已回退 Microsoft YaHei；若要更粗的黑体感可加「阿里巴巴普惠体/HarmonyOS Sans」本地字体。
- **jpg 序列编码**：帧文件名固定 `f%05d.jpg`，ffmpeg 用 `-framerate 30 -i f%05d.jpg`。
- **时长控制**：每幕 `dur` 之和 = 总时长；片头别超 5s，单幕别超 8s。配音版以音频时长为锚。
- **长后台被 kill**：单条后台命令总时长超过约 25–30 分钟会被任务管理器杀，拆分渲染段。
