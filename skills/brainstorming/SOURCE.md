# brainstorming — 安装来源与协作说明

> 本文件是安装记录，**不是**原版仓库内容。原版 8 个文件均字节级原样复制，未改一个字符。

## 来源

| 项目 | 内容 |
|------|------|
| 仓库 | `github.com/obra/superpowers`（Jesse Vincent） |
| 路径 | `skills/brainstorming/` |
| 安装时间 | 2026-09-09 |
| 安装位置 | `~/.workbuddy/skills/brainstorming/`（用户级，跨项目） |
| 文件 | SKILL.md / visual-companion.md / spec-document-reviewer-prompt.md / scripts/(server.cjs, helper.js, start-server.sh, stop-server.sh, frame-template.html) |

## 安全审计结论（本地实测，非转述）

| 检查项 | 结果 |
|--------|------|
| 监听地址 | 默认 `127.0.0.1` 回环，不暴露局域网 |
| 外连请求 | **零**（server.cjs 中 fetch/http.request 出现次数 = 0） |
| 路径穿越 | `isRegularFileInsideContentDir` 用 `realpathSync` + `startsWith` 双重校验 |
| 命令执行 | `child_process.exec` 仅在 `BRAINSTORM_OPEN_CMD` 时触发，且 HOST 为 localhost 时 **early-return 永不执行** |
| 写入范围 | 仅限会话 state 目录（/tmp/brainstorm），token 文件 0600，服务关闭时自动清理 |

⚠️ 不要设置 `BRAINSTORM_HOST=0.0.0.0`（会暴露到局域网，本机为公用电脑）。
⚠️ 服务默认不启动，只有显式执行 `scripts/start-server.sh` 才会占用端口。

## 与 grill-me 的分工（重要）

两个技能都会自动触发，为避免每件事过两道流程，按此顺序：

1. **grill-me 先跑** — 把需求/歧义问清楚（决策树、一轮一问、给推荐答案）
2. **brainstorming 后跑** — 需求清楚后分类（Spike / Bounded / Architectural），出设计，等批准
3. **HARD-GATE** — 未拿到 Yan 明确批准前，不写任何代码、不 scaffold、不动文件

边界（沿用既有约定）：
- **技术选型** → AI 直接拍板（给推荐+理由），Yan 只认可/否决
- **业务判断**（分类、洞察、方向取舍）→ Yan 拍板
- **简单/已固化任务**（改 typo、跑命令、生成 X 月 PPT）→ 不审问，直接执行

## 已知缺口

- Architectural 路径终点会调用 `writing-plans` 技能，**尚未安装**。等真正做架构级任务时再补装。
- 可回退：删掉 `~/.workbuddy/skills/brainstorming/` 目录即完全卸载。
