# 用户级长期记忆（跨项目）

## ⚠️ 电脑配置——务必区分新旧两台
- **新电脑（当前在用，2026-08-22 起）**
  - CPU: AMD Ryzen 5 9600X（6 核 12 线程）
  - 内存: 12 GB
  - GPU: NVIDIA RTX 5060 Ti 8 GB（nvidia-smi 实测 8GB；WMI 会误报 4GB，以 nvidia-smi 为准），CUDA 12
  - 磁盘: C 盘 144GB；**D 盘 333GB**。**2026-09-04 实测 C 盘仅剩 12-13GB（92% 满）**，清理后回到 22GB；做磁盘相关任务前先 `df -h /c`
  - **⚠️ 360 文件保护坑（必记）**：本机装了 360，删除操作会被拦截并送进回收站。后果是 **C→D 移动文件后 C 盘空间不会释放，必须再清空回收站才真正腾出空间**；另外 `du -sh /c/$Recycle.Bin` 读数不准（实测显示 3.8G，真实 9.6G），要以子目录 SID 目录逐项 du 为准
  - 活动盘约定: **用户明确要求以后活动都在 D 盘**（软件安装、模型、数据等）
  - Ollama: 程序 `D:\Ollama\ollama.exe`（含 `ollama app.exe` 托盘版）；模型存 `D:\Ollama\models`（用户级环境变量 `OLLAMA_MODELS=D:\Ollama\models`）；`D:\Ollama` 已加入用户 PATH
  - **已下载并验证可推理的模型**：`qwen2.5-coder:7b`（4.7GB，RTX 5060 Ti CUDA 加速正常，推理实测通过）
  - **代理坑**：本机环境挂了 `HTTP_PROXY/HTTPS_PROXY=127.0.0.1:10808` 但该代理当前未运行 → 拉模型会 `proxyconnect refused` 失败。解决：运行 ollama 时 `unset HTTP_PROXY HTTPS_PROXY`（已写入 `D:\Ollama\start-ollama.bat` 与启动文件夹 `start-ollama.cmd`）。本地推理已下载完不受影响。
  - **开机自启**：启动文件夹 `start-ollama.cmd` 自动拉起 D 盘 Ollama（原安装器 `.lnk` 指向已删的 C 盘路径，已失效）；手动启动也可双击 `D:\Ollama\ollama app.exe` 或跑 `D:\Ollama\start-ollama.bat`
  - **桌面路径被 360 重定向**：真实桌面是 `D:\360MoveData\Users\Administrator\Desktop`，**不是** `C:\Users\Administrator\Desktop`（Git Bash 的 `$USERPROFILE/Desktop` 找不到）。以后要在桌面放文件/快捷方式，直接用这个路径。已放桌面 `Ollama.lnk`（指向 `D:\Ollama\ollama app.exe` 托盘版）。
  - cc-haha: 配置 `C:\Users\Administrator\.claude\cc-haha\providers.json`，含 `ollama-local`（localhost:11434 / qwen2.5-coder:7b，默认）与 `moonshot`（kimi-k3）；用户级设置文件是 `C:\Users\Administrator\.claude\settings.json`（不是 `cc-haha\settings.json`），已写入 `alwaysThinkingEnabled: false` 以禁用 thinking 模式。
- **旧电脑（仍在用，切勿混淆）**
  - GPU: GTX 1660 6GB；内存 15.9GB
  - 旧 memory 中"本机有 Ollama + qwen2.5-coder:7b"指此机，**非**新电脑

## 软路由小主机（网络上的另一台设备）
- **iStoreOS（OpenWrt 系），管理地址 192.168.100.1**，root 密码 a8797796，与本机同网段、可 SSH
- **硬件实测（2026-09-12 修正）**：CPU **Intel Pentium 4417U @2.3GHz**（非 4415Y），双核四线程，支持 AES-NI；内存 **4GB**（无 swap）；NVMe 119.2G；4 网口（eth0=WAN 接光猫 192.168.68.0/24，eth1-3 空闲，br-lan=192.168.100.1）；主板 Super I/O = **ITE IT8772E**（hwmon4）；风扇插在 **fan2** 座
- **拓扑（重要）**：小主机是**光猫（192.168.68.1）下的二级路由**，和其他房间路由器是平级兄弟 → 只有它自己 LAN 侧（192.168.100.x，下面还挂一台 360 T5G）的设备受它管理。eth0 主地址 DHCP 192.168.68.135，另配了别名接口 wandns = **192.168.68.2**（固定，供全屋填 DNS）
- **2026-09-12 磁盘扩容**：overlay 已从 1.9G 扩到 **116.9G**（p3 扩到全盘），Docker Root Dir `/overlay/upper/opt/docker` 随之有 116.8G；已建 `/data`（download/media/backup/share/scripts/docker-compose）。坑：parted 对 busy 分区要用 `printf 'Yes\n' | parted ---pretend-input-tty ...`；ash 不支持 `{a,b}` 花括号展开
- **2026-09-12 全屋 DNS 去广告**：opkg 装 AdGuard Home 0.107.57；dnsmasq 让出 53 改到 **5354**；AdGuard 监听 0.0.0.0:53；管理页 **http://192.168.100.1:3000（admin / xifeng2026，建议改）**；规则 27.1 万条（源用 adguardteam.github.io + raw.githubusercontent.com，**jsdelivr/anti-ad.net 在这台机器不通**）；防火墙已放行 WAN 侧 53
  - **只去广告不管翻墙**；全屋翻墙需旁路网关 + mihomo 透明代理（现在 mihomo 是纯端口模式 redir-port=0）
  - **排障铁律：在路由器上 `curl -x 127.0.0.1:7892` 自测代理必返回 000**，mihomo 有 reject loopback 规则，不是代理坏了；要看 `/tmp/openclash.log` 里的 `using 主代理[节点]`
  - 回滚：`uci set dhcp.@dnsmasq[0].port='53'; uci commit dhcp; /etc/init.d/adguardhome stop; /etc/init.d/dnsmasq restart`
  - 详见 skill `istoreos-adguard-whole-home` / `istoreos-overlay-expand`
- 2026-09-11 修复：换 4 线 PWM 风扇后不转，根因是 IT8772E 自动温控曲线 50°C 以下输出 0 占空比
  - 小主机上已部署 `/etc/fancontrol.sh`（温度分档自动调速）+ cron 每 2 分钟执行，日志 `/tmp/fan.log`；开机自启走 `/etc/rc.local`
- **关机方式（重要，用户曾因直接断电搞崩系统）**：根文件系统是 ext4 overlay 在 NVMe 上，断电会写坏。**短按一下机身电源键 = 优雅关机**（/etc/rc.button/power → /sbin/poweroff）；**长按 4-5 秒是硬件强制断电，禁止**；LuCI 网页只有重启没有关机
  - 一键工具：`D:\Scripts\router.py`（status / poweroff / reboot）；**桌面小宠 `D:\Scripts\router_pet.py`**（PySide6，迷你模式/全屏自动隐藏/托盘/关机重启都在右键菜单），已设开机自启（Startup\Router-Pet.cmd），桌面快捷方式 = `路由小宠.lnk`（图标 D:\Scripts\pet.ico）；运行环境 D:\Python\petenv（PySide6-Essentials + paramiko + pywin32 venv）
- 本机 Windows 侧无 sshpass/plink，**远程登录这台机器要用 Python paramiko**（已装 5.0.0）；已配免密：本机 `~/.ssh/id_ed25519`（无口令）
  - 坑：Git Bash 的 ssh-keygen 写不进 `~/.ssh`（沙箱限制），先在工作区生成再用 PowerShell 拷过去

## 软路由 iStoreOS（192.168.100.1）运维要点
- root 密码 a8797796；系统 iStoreOS 24.10.8 / x86_64；本机用 paramiko 连（无 sshpass）
- OpenClash 0.47.156 + mihomo v1.19.30 内核（官方版，**无 smart 组**）
- **2026-09-12 定版架构：端口代理模式（国内永远直连，国外才走代理）**
  - OpenClash UI 显示「未运行」是**正常**的：已 `init.d disable` 自启，代理核心由 rc.local/manual `setsid` 起。**千万别点 UI「启动」**——它会按 UCI(fake-ip + 劫持 DNS)重新生成配置，把国内一起拖死（这是反复全断的元凶）。
  - 起核心：`setsid /etc/openclash/clash -d /etc/openclash -f /etc/openclash/config/MITCE.yaml`（YAML 需 `allow-lan:true` / `bind-address:'*'` / `redir-port:0` / `tproxy-port:0` / `external-controller:'0.0.0.0:9090'` / 无 `secret` / **`dns.listen: ''` 否则抢 53→全断**）
  - 改 rc.local / 配置**用 paramiko SFTP 直改文件**，不要用嵌套 sed（引号转义在 paramiko 下静默失效，曾导致 rc.local 只剩注释无启动行）
  - 控制 API：PC 直连 `http://192.168.100.1:9090`（无 secret）；切组 `PUT /proxies/主代理 {"name":"JP自动选择"}`
  - 已知坑：**两个 clash 实例并存**会导致 PC 经 7892 出网 502（路由器本地却 200），杀孤儿即可
  - PC 侧：系统代理走 PAC `C:\Users\Administrator\proxy_china.pac`（国内直连 + Windows 探针直连防弹回热点 + 国外→192.168.100.1:7892），两张网卡 DNS 静态 119.29.29.29/223.5.5.5
- **关键认知：mihomo 的 url-test/fallback 只按延迟(RTT)选节点，延迟低≠带宽高**，实测延迟最低节点可能比最快节点慢 35 倍
  → 已在路由器部署 `/usr/share/openclash/jp_speed.sh` 做真实下载测速 + 自动切换（cron 每 5 分钟）
- 从路由器测节点速度**不要走代理端口**（7893 需认证 `Clash:1PnrjBgd` 且 TLS 会失败），本机 curl 已被透明劫持，直连即可
- 订阅更新后主代理会重置，脚本 5 分钟内自动修正

## 重要约定
- 装软件、存数据优先 **D 盘**（用户硬性要求）。
- 涉及"本机 Ollama / 显卡 / 显存"时，先确认说的是哪台电脑；新电脑是 RTX 5060 Ti 8GB。
- cc-haha 桌面端服务商 Key: Moonshot 月之暗面标准 API（`api.moonshot.cn`，非 Kimi coding 端点），同一个 Key 在 OpenRouter 也可用。

## WorkBuddy 双机同步
- WorkBuddy 是账号制,但**用户级技能与记忆存在本机 `~/.workbuddy`,不跟账号走**(对话/个人画像云端同步)。双机互通需手动同步或中转方案。
- 已自建用户级技能 `workbuddy-cross-device-sync`(`~/.workbuddy/skills/`):纯标准库 `sync.py` + `SKILL.md`,`init` 配 folder/git 中转,`push`/`pull` 同步用户级技能+记忆,排除 `settings.json`/`mcp.json` 等敏感/缓存,覆盖前自动备份 `_backup`。两台都装本技能并指向同一中转即互通。
- **GitHub 中转已启用**:仓库 `https://github.com/gongtao0201-glitch/wb-skills-sync.git`(Private),走 HTTPS + 本机代理,凭证复用 GitHub Desktop 登录态。git 本地缓存位于 `~/.workbuddy/.wb-sync/repo`,避免与技能目录嵌套。

## Mac 设备（madeMac-mini.local，2026-09-26 接入）
- 这是一台 **macOS** 设备（Intel x86_64，macOS 12.7.6），**不是**上面说的 Windows「新电脑」。与 A 机（Windows）共享同一 WorkBuddy 账号与同步仓库，是双机互通的「另一台」。
- **跨设备同步改用 api 模式**：本机 git 通道被代理挡死（`git` 的 CONNECT 隧道返回 502 / HTTP2 帧错误），且 GitHub Desktop 存的钥匙串 service 名（`GitHub - https://api.github.com`）与 git 的 osxkeychain（`github.com`）不匹配，git 读不到令牌。故 `workbuddy-cross-device-sync` 的 `sync.py` 已改造支持 `api` 中转类型（走 `api.github.com`，代理与直连均放行，实测直连也是 200）。
- **令牌复用**：本机钥匙串已有 GitHub OAuth 令牌（来自浏览器登录），`sync.py` 的 `get_github_token()` 在 macOS 优先从钥匙串 `security find-generic-password -s "GitHub - https://api.github.com"` 读取，无需生成 PAT。
- **关键坑：`config.json` 每台机器独立，绝不参与同步**（已加入 `sync.py` 的 IGNORE 与 `_ignore_file`）。否则 A 机/Mac 的 remote/模式会互相覆盖，且可能泄漏本机令牌。sync.py 代码本身（共享逻辑）会同步，但 config 不会。
- 视频引擎 3 个（remotion-video-toolkit / wuding-kinetic-video / seedance）不在仓库，靠「兜底 zip」安装；仓库里的 skills 是其余共享技能。
- 用法：装好同步技能后 `init --type api --remote https://github.com/gongtao0201-glitch/wb-skills-sync.git`；发布端喊「同步」跑 `auto`，订阅端开机/定时跑 `pull`（覆盖前自动备份到 `_backup`）。
