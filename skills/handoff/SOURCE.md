# 安装来源与说明（非原版文件，不影响技能加载）

> 本目录下的 `SKILL.md` 与 `agents/openai.yaml` 为 **GitHub 原版字节级复制，未做任何改动**。
> 本文件仅作溯源与协作说明，可随时删除。

## 来源

| 项目 | 内容 |
|------|------|
| 仓库 | `github.com/mattpocock/skills`（作者 Matt Pocock） |
| 原版路径 | `skills/productivity/handoff/SKILL.md` |
| 安装路径 | `~/.workbuddy/skills/handoff/`（用户级，跨项目） |
| 安装日期 | 2026-09-09 |
| 校验 | `diff -r` 与原版逐字节比对 → 零差异 |

## 为什么选 `productivity/handoff` 而不是 `in-progress/claude-handoff`

仓库里有两个 handoff：

- **`skills/productivity/handoff/`**（正式版，本次安装）
  写 handoff 文档到 OS 临时目录，由人手动开新会话继续。**无任何外部依赖，WorkBuddy 可用。**
- `skills/in-progress/claude-handoff/`（实验版，**未安装**）
  直接执行 `claude --bg --name "xxx" "<summary>"` 启动后台 agent。
  **依赖 Claude Code CLI 的 `--bg` 参数——WorkBuddy 环境里没有 `claude` 命令，装了会断链。**

README 中 handoff 与 grill-me 同属 **User-invoked（手动调用）** 区，官方路径即 `skills/productivity/handoff/SKILL.md`。

## 触发方式：手动，不自动

- `SKILL.md` 有 `disable-model-invocation: true`
- `agents/openai.yaml` 有 `allow_implicit_invocation: false`

→ **模型不会自动触发**，必须 Yan 主动说 `/handoff` 或"handoff 一下"。
→ 因此不会与 grill-me / brainstorming 的自动触发冲突。

## 它会做什么

1. 把当前对话压缩成一份 handoff 文档，**保存到操作系统临时目录**（Windows 上是
   `C:/Users/Administrator/AppData/Local/Temp/`），**不写入当前 workspace**
2. 文档里含 **suggested skills** 段落，指明下一个 agent 该调用哪些技能
3. **不重复**已在其他 artifacts（specs / plans / ADRs / issues / commits / diffs）里的内容，只用路径或 URL 引用
4. **脱敏**：API keys、密码、个人身份信息一律隐去
5. 若带参数（如 `/handoff 继续修 login bug`），参数会被当作"下一轮会话的重点"来裁剪文档

## 与你现有技能的分工

| 技能 | 触发 | 作用 |
|------|------|------|
| grill-me | 自动（默认） | 动手前审问需求 |
| brainstorming | 自动（creative work） | 分类 + 出设计 + HARD-GATE |
| **handoff** | **手动** | **会话太长/要换会话时，压缩上下文给下一个 agent** |

## 注意点

- 原版指定**保存到系统临时目录**。如果你希望改成保存到工作区（如 `.workbuddy/handoff/`），
  告诉我一声即可改——但那会动原版正文，所以默认没改。
- 临时目录的文件系统重启/清理时可能丢失，重要的 handoff 记得自己另存。
