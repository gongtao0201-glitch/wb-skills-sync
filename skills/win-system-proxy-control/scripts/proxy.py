# -*- coding: utf-8 -*-
"""
Windows 系统代理(WinINET)程序化控制 —— 纯标准库，无第三方依赖。

用法:
  python proxy.py status                    # 查看当前代理状态
  python proxy.py direct                    # 清空代理 = 直连(最常用)
  python proxy.py set 192.168.1.2:7890      # 设为静态代理
  python proxy.py pac file:///C:/p.pac      # 设为 PAC 自动配置
  python proxy.py test                      # WinINET 实测出网(google/baidu)

原理要点:
  * Chrome/Edge 读的是 IE「连接」的二进制 blob，不是 AutoConfigURL 字符串值。
  * blob 有 DefaultConnectionSettings 和 SavedLegacySettings 两个，都要改。
  * blob 结构: DWORD cb | DWORD counter | DWORD dwAccessType | DWORD lenProxy | proxy[] |
                DWORD lenBypass | bypass[] | DWORD lenPac | pac[]
    dwAccessType @ offset 8 : 1=direct, 3=manual proxy, 5=PAC
  * InternetSetOptionW 必须传 NULL + 0，否则 rc=0/gle=12010。
"""
import ctypes
import struct
import sys
import time
import winreg

IE = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
CONN = IE + r"\Connections"
HKCU = winreg.HKEY_CURRENT_USER

ACCESS_DIRECT = 1
ACCESS_PROXY = 3
ACCESS_PAC = 5

ACCESS_NAME = {1: "direct(直连)", 3: "manual proxy(手动代理)", 5: "PAC(自动配置)"}

DEFAULT_BYPASS = ("<local>;localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;"
                  "172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;"
                  "172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*;100.64.*")


# ---------------- 注册表读写 ----------------
def get_val(path, name):
    try:
        k = winreg.OpenKey(HKCU, path)
        v, _ = winreg.QueryValueEx(k, name)
        winreg.CloseKey(k)
        return v
    except FileNotFoundError:
        return None


def set_val(path, name, value, typ):
    k = winreg.CreateKeyEx(HKCU, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
    try:
        winreg.SetValueEx(k, name, 0, typ, value)
    finally:
        winreg.CloseKey(k)


def del_val(path, name):
    try:
        k = winreg.OpenKey(HKCU, path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(k, name)
        winreg.CloseKey(k)
        return True
    except FileNotFoundError:
        return False


# ---------------- blob 构造 ----------------
def build_blob(access_type, proxy="", bypass="", pac=""):
    """构造 311 字节的 IE 连接 blob。"""
    p = proxy.encode("ascii", "replace")
    b = bypass.encode("ascii", "replace")
    c = pac.encode("ascii", "replace")
    out = bytearray()
    out += struct.pack("<I", 70)                 # cbHeader
    out += struct.pack("<I", int(time.time()) & 0xFFFFFFFF)  # counter
    out += struct.pack("<I", access_type)        # dwAccessType  @8
    out += struct.pack("<I", len(p)) + p         # proxy
    out += struct.pack("<I", len(b)) + b         # bypass
    out += struct.pack("<I", len(c)) + c         # pac
    out += b"\x00" * max(0, 311 - len(out))
    return bytes(out[:311])


def read_blob(name):
    v = get_val(CONN, name)
    if not isinstance(v, (bytes, bytearray)) or len(v) < 16:
        return None
    access = struct.unpack_from("<I", v, 8)[0]
    off = 12
    def take(buf, off):
        if off + 4 > len(buf):
            return "", len(buf)
        n = struct.unpack_from("<I", buf, off)[0]
        off += 4
        s = buf[off:off + n].decode("ascii", "replace").rstrip("\x00")
        return s, off + n
    proxy, off = take(v, off)
    bypass, off = take(v, off)
    pac, off = take(v, off)
    return {"access": access, "proxy": proxy, "bypass": bypass, "pac": pac, "len": len(v)}


# ---------------- 通知系统 ----------------
def notify():
    w = ctypes.windll.wininet
    r1 = w.InternetSetOptionW(None, 39, None, 0)   # SETTINGS_CHANGED
    r2 = w.InternetSetOptionW(None, 37, None, 0)   # REFRESH
    return r1, r2


# ---------------- 动作 ----------------
def apply(access_type, proxy="", bypass="", pac=""):
    # 1) 字符串值(给旧程序/IE 界面用)
    if access_type == ACCESS_DIRECT:
        set_val(IE, "ProxyEnable", 0, winreg.REG_DWORD)
        del_val(IE, "ProxyServer")
        del_val(IE, "AutoConfigURL")
        del_val(IE, "ProxyOverride")
    elif access_type == ACCESS_PROXY:
        set_val(IE, "ProxyEnable", 1, winreg.REG_DWORD)
        set_val(IE, "ProxyServer", proxy, winreg.REG_SZ)
        set_val(IE, "ProxyOverride", bypass or DEFAULT_BYPASS, winreg.REG_SZ)
        del_val(IE, "AutoConfigURL")
    elif access_type == ACCESS_PAC:
        set_val(IE, "ProxyEnable", 0, winreg.REG_DWORD)
        set_val(IE, "AutoConfigURL", pac, winreg.REG_SZ)
    # 2) 两个 blob
    blob = build_blob(access_type, proxy, bypass or DEFAULT_BYPASS, pac)
    for name in ("DefaultConnectionSettings", "SavedLegacySettings"):
        set_val(CONN, name, blob, winreg.REG_BINARY)
    # 3) 通知刷新
    return notify()


def status():
    print("ProxyEnable   =", get_val(IE, "ProxyEnable"))
    print("ProxyServer   =", get_val(IE, "ProxyServer"))
    print("ProxyOverride =", (get_val(IE, "ProxyOverride") or "")[:60], "...")
    print("AutoConfigURL =", get_val(IE, "AutoConfigURL"))
    for name in ("DefaultConnectionSettings", "SavedLegacySettings"):
        b = read_blob(name)
        if b:
            print(f"[{name}] len={b['len']} accessType={b['access']} "
                  f"({ACCESS_NAME.get(b['access'], '?')})")
            print(f"    proxy={b['proxy']!r}  pac={b['pac']!r}")
        else:
            print(f"[{name}] 不存在")


def test_wininet():
    print("=== WinINET 实测（读系统设置，等同浏览器路径）===")
    w = ctypes.windll.wininet
    w.InternetOpenW.restype = ctypes.c_void_p
    h = w.InternetOpenW("win-proxy-skill", 0, None, None, 0)
    if not h:
        print("  InternetOpen 失败")
        return
    for url in ("https://www.google.com", "https://www.baidu.com",
                "https://www.youtube.com"):
        hh = w.InternetOpenUrlW(ctypes.c_void_p(h), ctypes.c_wchar_p(url), None, 0, 0, 0)
        print(f"  {url} -> {'OK' if hh else 'FAIL'}")
        if hh:
            w.InternetCloseHandle(ctypes.c_void_p(hh))
    w.InternetCloseHandle(ctypes.c_void_p(h))


def verify_stable(seconds=18, step=6):
    """复查代理设置是否被其他软件回写。"""
    rounds = max(1, seconds // step)
    for i in range(rounds):
        b = read_blob("DefaultConnectionSettings")
        at = b["access"] if b else "?"
        print(f"[check{i+1}] ProxyEnable={get_val(IE, 'ProxyEnable')} "
              f"ProxyServer={get_val(IE, 'ProxyServer')} "
              f"accessType={at} ({ACCESS_NAME.get(at, '?')})")
        if i < rounds - 1:
            time.sleep(step)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd = args[0].lower()

    if cmd == "status":
        status()
    elif cmd == "direct":
        print("[before]"); status()
        print("[apply] rc =", apply(ACCESS_DIRECT))
        print("[after]"); status()
        verify_stable()
        test_wininet()
        print("\n提示：把浏览器全部窗口关掉再重开，才会完全生效。")
    elif cmd == "set":
        if len(args) < 2:
            print("用法: python proxy.py set host:port"); return
        print("[apply] rc =", apply(ACCESS_PROXY, proxy=args[1]))
        status()
        verify_stable()
        test_wininet()
    elif cmd == "pac":
        if len(args) < 2:
            print("用法: python proxy.py pac file:///C:/x.pac"); return
        print("[apply] rc =", apply(ACCESS_PAC, pac=args[1]))
        status()
        verify_stable()
    elif cmd == "test":
        test_wininet()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
