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
| `pull` | 从远端拉最新并覆盖本机(覆盖前自动备份) |
| `status` | 对比本机与远端 |
| `doctor` | 检查环境(git / 代理 / 远端配置) |

## 首次使用(每台电脑做一次)
1. 把本技能目录 `workbuddy-cross-device-sync` 放到两台电脑的 `~/.workbuddy/skills/`(用 `wb-sync-skill.zip` 解压,或一端 push 后另一端 pull)。
2. **GitHub Desktop 登录**(只需做一次, 全局有效):
   - 在两台电脑都打开 GitHub Desktop,登录**同一个 GitHub 账号**。
   - 国内访问走本机 `HTTPS_PROXY` 代理(脚本自动继承);SSH 22 端口通常被墙,**务必用 HTTPS URL 而非 SSH**。
3. 在其中一台运行 `init --type git --remote https://github.com/<你>/wb-skills-sync.git`。脚本会自动检查仓库是否存在,不存在则自动创建私有仓库。
4. "源电脑"(技能/记忆全的那台)运行 `push`,把初始大脑推上仓库。git 本地缓存放在 `~/.workbuddy/.wb-sync/repo`,不与技能目录互相嵌套。

## 自动化(实现你要的"自动互通")
装好技能后,在**两台电脑**各建一个周期性自动化任务(在 WorkBuddy 里让我创建,或你自己建):
- 频率:每 15 分钟
- 任务提示:"运行跨设备同步:用 WorkBuddy 托管 Python 执行 `~/.workbuddy/skills/workbuddy-cross-device-sync/sync.py pull` 然后 `push`,把本机技能/记忆与 GitHub 私有仓库对齐。若发现远端有新技能,拉取后提示用户重启 WorkBuddy 以加载。"

效果:
- **新增一个技能** → 15 分钟内自动 push 上云,另一台自动 pull 得到。
- **每次打开 WorkBuddy** → 最近 15 分钟内已自动 pull 过,基本是最新;若想即时,开场说一句"同步 pull"即可。

## 安全须知
- **绝不同步** `settings.json` / `mcp.json`(含 API key / OAuth 令牌)、`node_modules`、`__pycache__`、`*.log`。
- 每次覆盖目标前,自动把被覆盖内容备份到技能目录 `_backup/<时间戳>/`,误覆盖可手动找回。
- 中转仓库请设为**私有**(Private)。
- 同一时刻尽量只在一台改"大脑",避免互盖;git 模式用 rebase,若冲突会提示手动解决。

## 注意事项
- 国内网络:GitHub 走 HTTPS + 代理(脚本自动继承 `HTTPS_PROXY`);SSH(22 端口)通常不可达,别用 `git@github.com:...` 形式。
- 连接器(MCP / OAuth)同步后多半需重新授权一次,属正常。
- 用户名不同的两台 Windows 同步的是 `~/.workbuddy` 内容本身,与用户名无关,可正常互通。
