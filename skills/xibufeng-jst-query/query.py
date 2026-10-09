# -*- coding: utf-8 -*-
"""
西部风聚水潭数据查询 —— 统一入口

用法：
    python query.py shop-list                      # 店铺列表
    python query.py sales     --days 30 --top 10   # 销量/销售额排行
    python query.py shop      --days 30            # 分平台对比
    python query.py refund    --days 30            # 退货分析
    python query.py inventory                      # 库存
    python query.py item      --keyword 窝料       # 商品档案（含成本价）
    python query.py diagnose                       # 自检：哪些接口能用

所有子命令都支持 --json 输出原始 JSON（供程序处理）。
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

try:
    from jst_client import JSTClient, JSTError
except ImportError as e:
    print(f"找不到 jst_client.py，请确认本文件和 jst_client.py 在同一目录。\n错误：{e}")
    sys.exit(2)

HERE = Path(__file__).parent

INTERFACES = {
    "sales":     ("/open/orders/out/simple/query", "销售出库查询", "出库API"),
    "orders":    ("/open/orders/single/query", "订单查询", "订单API"),
    "inventory": ("/open/inventory/query", "商品库存查询", "库存API"),
    "refund":    ("/open/refund/single/query", "售后退货退款查询", "售后API"),
    "item":      ("/open/sku/query", "普通商品资料查询(按sku)", "商品API"),
    "category":  ("/open/category/query", "商品类目查询", "商品API"),
    "shops":     ("/open/shops/query", "店铺查询", "基础API"),
}


class NoPermission(Exception):
    pass


def call(client, key, biz):
    """调用接口，把权限不足单独识别出来，给出可操作提示"""
    path, name, catalog = INTERFACES[key]
    try:
        return client.request(path, biz)
    except JSTError as e:
        msg = str(e)
        if "190" in msg or "无API权限" in msg or "无权限" in msg:
            raise NoPermission(
                f"接口「{name}」({path}) 还没有申请权限。\n"
                f"    → 去聚水潭开放平台：应用详情 → API接口权限 → 目录选「{catalog}」→ 勾选「{name}」→ 一键申请\n"
                f"    → 审批通常 5 分钟内，批完重试即可"
            )
        raise


def load_shop_names(client):
    names = {}
    try:
        for s in client.get_shops():
            names[s.get("shop_id")] = s.get("shop_name") or s.get("nick") or f"shop_id={s.get('shop_id')}"
    except (JSTError, NoPermission):
        pass
    return names


def date_range(days):
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fmt_money(v):
    return f"&yen;{v:,.2f}"


# ---------------- 子命令 ----------------

def cmd_shop_list(client, args):
    shops = client.get_shops()
    if args.json:
        print(json.dumps(shops, ensure_ascii=False, indent=2))
        return
    print(f"共 {len(shops)} 个店铺：\n")
    print(f"{'shop_id':<12}{'平台':<12}{'店铺名称'}")
    print("-" * 70)
    for s in shops:
        print(f"{s.get('shop_id'):<12}{str(s.get('shop_site') or '-'):<12}{s.get('shop_name')}")


def cmd_sales(client, args):
    start, end = date_range(args.days)
    print(f"统计区间：{start} ~ {end}\n")
    result = call(client, "sales", {"start_ts": 1, "is_get_total": False,
                                    "page_index": 1, "page_size": 100})
    orders = result.get("data", {}).get("orders", []) or []
    if args.json:
        print(json.dumps(orders[:50], ensure_ascii=False, indent=2))
        return
    if not orders:
        print("这个区间没有出库单。")
        return
    print(f"拉到 {len(orders)} 张出库单，字段示例：")
    print(json.dumps(orders[0], ensure_ascii=False, indent=2)[:1500])


def cmd_shop(client, args):
    print("分平台对比需要「销售出库查询」权限，当前待开通后可自动分析。")
    cmd_sales(client, args)


def cmd_refund(client, args):
    start, end = date_range(args.days)
    result = call(client, "refund", {"page_index": 1, "page_size": 100,
                                     "start_time": start, "end_time": end})
    refunds = result.get("data", {}) or {}
    print(json.dumps(refunds, ensure_ascii=False, indent=2)[:1500])


def cmd_inventory(client, args):
    result = call(client, "inventory", {"page_index": 1, "page_size": 100})
    data = result.get("data", {}) or {}
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])


def cmd_item(client, args):
    biz = {"page_index": 1, "page_size": 100}
    if args.keyword:
        biz["name"] = args.keyword
    else:
        # 商品接口要求时间范围，默认查最近 7 天（接口限制单次跨度≤7天）
        s, e = date_range(7)
        biz["modified_begin"] = s + " 00:00:00"
        biz["modified_end"] = e + " 23:59:59"
    result = call(client, "item", biz)
    data = result.get("data", {}) or {}
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])


def cmd_diagnose(client, args):
    print("接口权限自检：\n")
    ok = no = 0
    for key, (path, name, catalog) in INTERFACES.items():
        try:
            client.request(path, {"page_index": 1, "page_size": 1})
            print(f"  [可用]   {name}  ({catalog})")
            ok += 1
        except JSTError as e:
            msg = "无API权限（未申请）" if ("190" in str(e) or "无API权限" in str(e)) else str(e)[:40]
            print(f"  [不可用] {name}  ({catalog})  → {msg}")
            no += 1
    print(f"\n可用 {ok} 个，不可用 {no} 个")
    if no:
        print("\n去聚水潭开放平台 → 应用详情 → API接口权限 → 按上面标注的目录勾选申请。")


COMMANDS = {
    "shop-list": cmd_shop_list, "sales": cmd_sales, "shop": cmd_shop,
    "refund": cmd_refund, "inventory": cmd_inventory, "item": cmd_item,
    "diagnose": cmd_diagnose,
}


def main():
    ap = argparse.ArgumentParser(description="西部风聚水潭数据查询")
    ap.add_argument("command", choices=list(COMMANDS.keys()), help="查询类型")
    ap.add_argument("--days", type=int, default=30, help="统计天数，默认30")
    ap.add_argument("--top", type=int, default=10, help="前N名，默认10")
    ap.add_argument("--keyword", help="商品名称关键词")
    ap.add_argument("--json", action="store_true", help="输出原始JSON")
    args = ap.parse_args()

    try:
        client = JSTClient()
    except ValueError as e:
        print(f"配置问题：{e}\nconfig.json 应放在本文件同目录：{HERE / 'config.json'}")
        sys.exit(2)
    except JSTError as e:
        print(f"连接聚水潭失败：{e}")
        sys.exit(1)

    try:
        COMMANDS[args.command](client, args)
    except NoPermission as e:
        print(f"\n{e}")
        sys.exit(3)
    except JSTError as e:
        print(f"查询失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
