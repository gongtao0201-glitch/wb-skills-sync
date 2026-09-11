---
name: win-system-proxy-control
description: 在 Windows 上程序化读取 / 设置 / 清除系统代理（WinINET），包括修改 IE「连接」二进制 blob 与 InternetSetOption 刷新。用于「浏览器报 ERR_EMPTY_RESPONSE / ERR_CONNECTION_TIMED_OUT 但命令行 curl 正常」「想让浏览器走/不走代理」「360 锁代理设置」等场景。
agent_created: true
---

# Windows 系统代理程序化控制

## 何时用
- 浏览器打不开某站，但 `curl` 直连是 200 → 说明**浏览器在走一个坏代理**，先查系统代理。
- 想给浏览器挂/摘代理，又不想让用户点 GUI（尤其装了 360，GUI 会被"上网保护"改回去）。
- 排查 `ERR_EMPTY_RESPONSE`（代理端口接受连接但回空）、`ERR_CONNECTION_TIMED_OUT`（代理端口不通）。

## 核心事实（血泪）
1. **Chrome/Edge 在 Windows 上读的是 IE「连接」的二进制 blob**，不是 `AutoConfigURL` 这个字符串值。
   → 只写 `AutoConfigURL` 完全无效。
2. blob 有两个：`DefaultConnectionSettings`（当前）和 `SavedLegacySettings`（保存的旧配置），**两个都要改**，否则可能被回滚。
3. blob 结构（总长 311 字节）：
   ```
   DWORD cbHeader | DWORD dwCounter | DWORD dwAccessType | DWORD lenProxy | proxy[] |
   DWORD lenBypass | bypass[] | DWORD lenPac | pac[]
   ```
   - dwAccessType @ **offset 8**：`1`=直连、`3`=手动代理、`5`=PAC
4. `InternetSetOptionW` 通知刷新时**参数必须 NULL + 0**：
   ```python
   wininet.InternetSetOptionW(None, 39, None, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
   wininet.InternetSetOptionW(None, 37, None, 0)  # INTERNET_OPTION_REFRESH
   ```
   → 传结构体会得到 `rc=0 / gle=12010 (INVALID_PARAMETER)`，别误判成"被 360 锁了"。
5. 排查顺序：查进程（v2rayN/xray/clash 会抢系统代理） → 查注册表 → 查 Chrome `User Data\Default\Preferences` 的 `proxy` 键（浏览器级） → 才怀疑 SwitchyOmega 类扩展。

## 一键脚本
`scripts/proxy.py`（纯标准库，无第三方依赖）：

```bash
python scripts/proxy.py status              # 看当前代理状态
python scripts/proxy.py direct              # 清空代理 = 直连（最常用）
python scripts/proxy.py set 192.168.1.2:7890  # 设为静态代理
python scripts/proxy.py pac file:///C:/p.pac  # 设为 PAC
python scripts/proxy.py test                # WinINET 实测 google/baidu
```

## 典型场景：路由器 TUN 透明代理 + PC 不该有代理
OpenClash / mihomo 用 fake-ip + TUN 时，PC 侧正确终态是**无代理**。
若 PC 还留着 `ProxyServer=<路由器IP>:7892`，浏览器会走那条显式代理路 → 该路在 TUN 模式下往往不通 → `ERR_EMPTY_RESPONSE`。
而 `curl`（不读 WinINET）走透明代理是 200，形成"curl 通、浏览器不通"的经典分裂。**修法：`proxy.py direct`，然后关掉浏览器窗口重开。**

## 验证必须用浏览器本体
`curl` 不走 WinINET，验证不了浏览器行为。用无头 Chrome 复现：
```bash
chrome.exe --headless=new --disable-gpu --no-first-run \
  --user-data-dir="$TEMP\chrome-proxy-test" --virtual-time-budget=9000 \
  --dump-dom https://www.youtube.com | head -c 300
```
返回真实页面 DOM = 通；返回错误页/空 = 不通。

## 注意
- 写注册表后**等 15~20 秒复查 2~3 次**，确认没被 360 之类的软件回写。
- `reg.exe` 可能被沙箱拦；用 Python `winreg` 即可。
- 改之前先打印 before 值，方便回滚。
