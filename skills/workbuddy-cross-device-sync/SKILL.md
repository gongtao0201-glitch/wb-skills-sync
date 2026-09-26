---
name: workbuddy-cross-device-sync
description: 让两台(或多台)登录同一 WorkBuddy 账号的电脑共享"大脑"——用户级技能与用户级记忆互通。装到两台电脑并指向同一个中转位置后,新增技能自动上传云端、每次打开 WorkBuddy 自动拉取新技能,两台行为一致。适用于家庭/公司异地双机党。推荐 GitHub 私有仓库作中转。
---

# WorkBuddy 跨设备同步技能

## 解决什么问题
WorkBuddy 是账号制,但**用户级技能和记忆存在本机 `~/.workbuddy/` 里,不跟账号走**。换电脑或双机异地共用时,技能和记忆不会自动互通。本技能把"大脑"(用户级技能 + 用户级记忆)推到 / 拉自一个**中转位置**,两台电脑装本技能后共享该中转,实现互通。

## 中转选择
- **GitHub 私有仓库(推荐, 跨网/跨地点)**: `remote` 填 `https://github.com/<你>/wb-skills-sync.git`。走本机代理,凭证复用 GitHub Desktop 登录。
- folder: 局域网共享目录 / 云盘同步空间(同地点用,零外部依赖)。
- **api(代理环境救星)**: `remote` 填同样的 GitHub 仓库 URL, 但 `init --type api`。脚本直接用 GitHub REST API 操作仓库(走 `api.github.com`, 代理/直连都放行), 令牌自动从本机取(macOS 钥匙串 `"GitHub - https://api.github.com"` / Windows `git credential fill` / 或 config.json 的 `token` 字段), **无需 git 二进制**。适合 macOS 上 git 通道被代理挡死、装不了 GitHub Desktop 的场景。

## 触发词(在对话中说)
- "同步技能" / "同步记忆" / "跨设备同步" / "把技能同步到另一台电脑"
- "配置同步中转" / "检查同步状态"
- "wb-sync push" / "wb-sync pull"

检测意图后,用 WorkBuddy 自带的托管 Python 运行本技能目录下的 `sync.py`:
```
<managed python> <技能目录>/sync.py <子命令>
```

## 子命令
| 命令 | 作用 |
|------|------|
| `init --type git --remote <仓库URL>` | 配置中转为 GitHub 仓库 |
| `init --type folder --remote <目录>` | 配置中转为共享/同步盘目录 |
| `push` | 先 pull 远端最新,再把本机大脑推上去(有变更才 commit/push) |
| `auto` | **发布端推荐**:先对技能/MEMORY.md/memory 做内容哈希快照,仅当检测到新增/改动时才 push(无变更直接跳过,不空跑) |
| `pull` | 从远端拉最新并覆盖本机(覆盖前自动备份) |
| `status` | 对比本机与远端 |
| `doctor` | 检查环境(git / 代理 / 远端配置) |

## 首次使用(每台电脑做一次)
1. 把本技能目录 `workbuddy-cross-device-sync` 放到两台电脑的 `~/.workbuddy/skills/`(用 `wb-sync-skill.zip` 解压,或一端 push 后另一端 pull)。
2. **GitHub Desktop 登录**(只需做一次, 全局有效):
   - 在两台电脑都打开 GitHub Desktop,登录**同一个 GitHub 账号**。
   - 国内访问走本机 `HTTPS_PROXY` 代理(脚本自动继承);SSH 22 端口通常被墙,**务必用 HTTPS URL 而非 SSH**。
3. 在其中一台运行 `init --type git --remote https://github.com/<你>/wb-skills-sync.git`。脚本会自动检查仓库是否存在,不存在则自动创建私有仓库。**(若 git 通道不通 / 没装 git / 装不了 GitHub Desktop, 改用 `init --type api --remote <同一URL>` ——走 GitHub API, 零 git 依赖。)**: 
4. "源电脑"(技能/记忆全的那台)运行 `push`(或 `auto`),把初始大脑推上仓库。git/api 模式不落本地仓库缓存;folder 模式直接写共享目录。

## 自动化(实现你要的"发布-订阅"互通)
核心原则:**谁改了谁上传,对方按需/开机拉取**,避免两台机器定时双向 pull+push 互相无脑覆盖、制造假冲突。

- **发布端(技能被新建/修改的机器)**:建一个周期性自动化,只跑 `auto`(变更检测后才 push,无变更不空跑)。
  - 频率:每 1 小时(或任意你接受的频率)
  - 提示:"用托管 Python 执行 `sync.py auto`。检测到新增/改动技能才推到 GitHub 私有仓库;无变更跳过。若推送了新技能,提醒另一台机器去巡检拉取。"
- **订阅端(另一台机器)**:不定时双向跑,改为两种触发拉取:
  - ① **开机巡检一次**:在 Windows 任务计划里建"登录时"触发,跑 `sync.py pull`(覆盖前自动备份);或让 WorkBuddy 在你登录时跑一次 pull。
  - ② **按需巡检**:你随时说"巡检/同步",我主动跑 `sync.py pull` 把远端新技能下载到本机。

效果:
- **本机新增一个技能** → 自动化的 `auto` 在下个周期检测到变更即 push 上云;另一台下次开机巡检 / 你喊"巡检"时 pull 得到。
- **不再无脑互相覆盖**:pull 只在订阅端显式触发,不会和发布端的 push 打架。

## 安全须知
- **绝不同步** `settings.json` / `mcp.json`(含 API key / OAuth 令牌)、`config.json`(本机 remote/模式/可选 token, 每台机器独立)、`node_modules`、`__pycache__`、`*.log`。
- 每次覆盖目标前,自动把被覆盖内容备份到技能目录 `_backup/<时间戳>/`,误覆盖可手动找回。
- 中转仓库请设为**私有**(Private)。
- 同一时刻尽量只在一台改"大脑",避免互盖;git 模式用 rebase,若冲突会提示手动解决。

## 注意事项
- 国内网络:GitHub 走 HTTPS + 代理(脚本自动继承 `HTTPS_PROXY`);SSH(22 端口)通常不可达,别用 `git@github.com:...` 形式。
- 连接器(MCP / OAuth)同步后多半需重新授权一次,属正常。
- 用户名不同的两台 Windows 同步的是 `~/.workbuddy` 内容本身,与用户名无关,可正常互通。
