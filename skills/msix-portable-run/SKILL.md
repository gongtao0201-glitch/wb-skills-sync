---
name: msix-portable-run
description: 绕过 Windows 系统版本限制，把 MSIX/APPX 应用包当 ZIP 解压后直接运行（"免安装绿色版"）。当 MSIX 因 MinVersion 高于当前系统版本装不上、或不想走微软商店、或需要绿色便携版时使用。也可用于从任何 MSIX 包里提取主程序、查系统要求、做离线部署。
agent_created: true
---

# MSIX 免安装解压运行

## 适用场景

- MSIX 安装报 `MinVersion` 不满足（如应用要求 19041，系统是 18363）
- 用户明确要求"不通过微软商店"安装
- 需要绿色版 / 便携版 / 免注册表安装
- 想先确认一个 MSIX 包到底要求什么系统版本再决定要不要升级

## 核心原理

MSIX 就是一个 ZIP。清单 `AppxManifest.xml` 里若同时满足：

1. `TargetDeviceFamily` 的 `MinVersion` 高于当前系统 → **无法安装**
2. `Dependencies` 为空 或 依赖已在本机 → **自包含**
3. `Application` 的 `EntryPoint="Windows.FullTrustApplication"` → **标准 Win32 程序**

那就可以跳过安装，直接解压运行主程序。Chromium/Electron 类应用（ChatGPT、各类 Electron 客户端）几乎都符合。

## 标准流程

### Step 1 — 拿到官方 MSIX 直链

优先找厂商自己的 CDN。已验证可用的：

```
ChatGPT 新版 (OpenAI.Codex, x64):
https://persistent.oaistatic.com/codex-app-prod/ChatGPT-x64.msix
```

其他来源：
- 厂商开发者文档里的企业离线部署页（搜 `<产品> enterprise windows deployment msix`）
- `store.rg-adguard.net` 的 GetFiles API **已失效（403）**，别浪费时间

### Step 2 — 下载

```bash
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131" \
  -o app.msix "<URL>"
```

大包用 `run_in_background`，734 MB 约 2 分钟。

### Step 3 — **本地**解析清单（不要远程解析）

远程 range 读 ZIP64 会踩坑（EOCD 字段是 0xFFFFFFFF 哨兵值、416 Range Not Satisfiable）。
**先下载，再用 `zipfile` 本地解析**：

```python
import zipfile, re
z = zipfile.ZipFile(r"D:\pkg\app.msix")
xml = z.read("AppxManifest.xml").decode("utf-8")
print(re.findall(r"<Identity[^>]*/?>", xml))
print(re.findall(r"<TargetDeviceFamily[^>]*/?>", xml))   # ← MinVersion 在这里
print(re.findall(r"<PackageDependency[^>]*/?>", xml))
print(re.findall(r"<Application[^>]*>", xml))            # ← Executable 是主程序
```

当前系统版本：`Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'`
取 `CurrentBuild`（如 18363 = Win10 1909，19041 = 2004）。

### Step 4 — 解压

```python
import zipfile, os
with zipfile.ZipFile(src) as z:
    for info in z.infolist():
        try: z.extract(info, dst)
        except Exception as e: print("跳过 %s: %s" % (info.filename, e))
```

node_modules 类超长路径会报 `WinError 206 文件名太长`，**跳过即可**，不影响主程序。

### Step 5 — 实跑验证

```powershell
$p = Start-Process -FilePath "<exe>" -PassThru
Start-Sleep -Seconds 12
$a = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
# 检查 $a.MainWindowTitle / $a.Responding
```

### Step 6 — 建入口（关键陷阱）

**不要用 `.lnk` 扩展名的符号链接！** Explorer 会把符号链接内容当 LNK 二进制解析 → 失败。

正确做法 —— 用 **`.exe` 扩展名的符号链接**：

```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\Desktop\App.exe" `
  -Target "D:\App\app\App.exe" -Force
```

系统会跟随链接执行真实程序，图标自动继承。开始菜单同理：
`"$env:APPDATA\Microsoft\Windows\Start Menu\Programs\App.exe"`

> 用 `New-Object -ComObject WScript.Shell` 建真 .lnk **会被安全策略拦截**，别走这条路。

### Step 7 — 提供更新脚本

解压版不会自动更新。写个 bat：taskkill → 重新下载 → 解压到 `App_new` →
**旧目录 move 成 `App_old_日期`（不删除）** → `App_new` 改名为 `App`。
符合"删除前必须确认"的铁律。

## 已知限制（要如实告知用户）

- 无自动更新，需手动跑更新脚本
- 应用内可能弹"请到商店更新"的提示，忽略即可
- 不注册文件关联 / URI 协议（部分深度集成功能可能失效）
- 全局热键（如 Alt+Space）由应用自行注册，通常可用

## 本机环境备忘（Yan 的机器）

- Windows 10 Pro **18363.418**（1909）
- **无 App Installer → winget 不可用**
- MSIX 框架依赖齐全：VCLibs 14.0.33519 / UI.Xaml 2.8 / WindowsAppRuntime 1.8、2.4
- 已装：ChatGPT 免安装版 → `D:\ChatGPT\App\app\ChatGPT.exe`
