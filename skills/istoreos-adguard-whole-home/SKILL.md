---
name: istoreos-adguard-whole-home
description: 在 iStoreOS / OpenWrt 软路由上部署 AdGuard Home 做全屋 DNS 去广告，包括让出 53 端口、防火墙放行 WAN 侧、配置固定 DNS 地址、设置管理密码，以及排查"改完 DNS 翻墙是不是坏了"。当提到全屋去广告、AdGuard Home、DNS 拦截、广告过滤、其他房间的设备也要生效时触发。
agent_created: true
---

# iStoreOS 全屋 DNS 去广告（AdGuard Home）

## 架构前提

先搞清楚拓扑：`ip route` 看上游网关，`ip -br addr` 看网口。
小主机常常是"光猫下的二级路由"，此时**其他房间的设备和它平级，流量不过它**。
DNS 层方案（本 skill）能让全屋去广告但**不管翻墙**；翻墙需要旁路网关 + 透明代理，是另一件事。

## 安装

```sh
opkg update && opkg install adguardhome    # 官方源自带，0.107.x，别折腾 Docker
```

路径：二进制 `/usr/bin/AdGuardHome`，配置 `/etc/adguardhome.yaml`，
workdir `/var/lib/adguardhome`，procd init `/etc/init.d/adguardhome`。

## 关键坑（按踩坑顺序）

### 1. opkg 安装后服务会自动启动 —— 会停在首次安装向导

安装瞬间就启动了，此时还没有你的配置，它会在 3000 端口等向导。
**正确顺序**：安装 → 写配置 → 停服务 → 传配置 → 启服务。
只看 `ps` 有进程不代表配置生效，用 `/control/status` 或规则数确认。

### 2. dnsmasq 占着 53，必须让出来

```sh
uci set dhcp.@dnsmasq[0].port='5354'   # 保留 DHCP 和本地 .lan 解析
uci commit dhcp && /etc/init.d/dnsmasq restart
```

AdGuard 上游里把本地域名指回 dnsmasq：
```yaml
- "[/lan/]127.0.0.1:5354"
- "[/100.168.192.in-addr.arpa/]127.0.0.1:5354"
```

副作用：`localuse=1` 时 `/etc/resolv.conf` 变成 `127.0.0.1`，
**路由器自己**的 DNS 也会走 AdGuard。若代理核心（mihomo）的
`default-nameserver` 含 `system`，节点域名可能被过滤规则误伤 →
表现为翻墙失效。排查时用光猫 DNS 对比解析节点域名，一致则无关。

### 3. WAN 侧默认访问不到 53（zone input REJECT）

其他网段设备要用到，必须放行：

```sh
uci batch <<'EOF'
add firewall rule
set firewall.@rule[-1].name='AdGuard-DNS-from-WAN'
set firewall.@rule[-1].src='wan'
set firewall.@rule[-1].proto='tcp udp'
set firewall.@rule[-1].dest_port='53'
set firewall.@rule[-1].target='ACCEPT'
set firewall.@rule[-1].family='ipv4'
commit firewall
EOF
/etc/init.d/firewall reload
```

### 4. 规则源：jsdelivr / anti-ad.net 在国内小主机上常常不通

实测（2026-09，成都电信）可用：
- `https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt`（4.3MB，17.8 万条）
- `https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-easylist.txt`（2MB，9.2 万条）

不可用：`cdn.jsdelivr.net`、`anti-ad.net`、`gitee.com`（404）。
**部署前先 curl 测源**，别直接抄网上教程的 URL。

### 5. 刷新规则的 API 不是 /control/update_filters

```sh
curl -X POST 'http://127.0.0.1:3000/control/filtering/refresh?force=1'
curl http://127.0.0.1:3000/control/filtering/status   # 看 rules_count
```

`rules_count: 0` 就是规则没下载下来，去广告等于没开。

### 6. 设管理密码：install API 在非首次启动时返回 404

`POST /control/install/configure` 只在"配置文件不存在"时注册。
配置文件已存在时，**只能手写 bcrypt 到 yaml**：

```python
import bcrypt; print(bcrypt.hashpw(b'密码', bcrypt.gensalt(rounds=10)).decode())
```

```yaml
users:
  - name: admin
    password: '$2b$10$...'    # 必须加引号，$ 和 / 会破坏 YAML/sed
```

sed 改这个文件会失败（hash 里的 `/` 和 `$`），用脚本下载-改-上传。
验证：无认证访问 `http://x:3000/control/status` 应返回 403。

### 7. ⚠️ 在路由器上自测代理必失败（reject loopback）

```sh
curl -x http://127.0.0.1:7892 https://www.google.com    # 一定返回 000
```

mihomo 有 `reject loopback` 规则，日志会写
`dial DIRECT (match RuleSet/Local-IP) ... error: reject loopback connection`。
**这不是代理坏了**。判断代理是否真的挂了要看 `/tmp/openclash.log`：
有 `using 主代理[节点名]` 且没有对应 error 就是正常的。

## 给用户一个不会变的 DNS 地址

小主机 WAN 是 DHCP，IP 会变 → 其他路由器填的 DNS 会失效。
用别名接口加一个固定地址，零断网风险：

```sh
uci batch <<'EOF'
set network.wandns=interface
set network.wandns.proto='static'
set network.wandns.device='@wan'
set network.wandns.ipaddr='192.168.68.2'
set network.wandns.netmask='255.255.255.0'
commit network
EOF
uci add_list firewall.@zone[1].network='wandns'   # 索引按实际 wan zone 定
uci commit firewall
ifup wandns        # 只起这一个接口，不动主 WAN
```

选地址前先 ping 探测，避开 DHCP 池（一般从 .100 起，选 .2 之类）。

## 验收清单

```sh
nslookup pos.baidu.com 192.168.68.2     # 广告域名 -> 0.0.0.0
nslookup www.baidu.com 192.168.68.2     # 正常域名 -> 真实 IP
curl -s -o /dev/null -w '%{http_code}' https://www.baidu.com   # 200
curl -s -u admin:密码 http://127.0.0.1:3000/control/filtering/status
```

## 回滚

```sh
uci set dhcp.@dnsmasq[0].port='53'; uci commit dhcp
/etc/init.d/adguardhome stop; /etc/init.d/dnsmasq restart
```
