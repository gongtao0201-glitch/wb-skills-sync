# -*- coding: utf-8 -*-
"""
查本机直连公网出口IP —— 聚水潭 IP 白名单就填这个。

    python check_ip.py

注意：必须查【绕过代理后】的IP。开着 v2rayN 时直接百度搜"IP"会显示境外节点，
填那个会被聚水潭拒绝。
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

from jst_client import get_public_ip

if __name__ == "__main__":
    print("=" * 55)
    print("聚水潭 IP 白名单填这个值 ↓")
    print("=" * 55)
    print(get_public_ip())
    print("=" * 55)
    print("提示：宽带重拨后 IP 可能变化，调不通时重跑本脚本。")
