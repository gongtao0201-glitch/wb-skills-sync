# -*- coding: utf-8 -*-
"""
聚水潭开放平台 API 客户端
零第三方依赖 —— 只用 Python 标准库，无需 pip install

签名规则（官方 docId=70 确认）：
    sign = MD5( app_secret + "key1value1key2value2..." ).hexdigest()  → 32位小写
    · 按 key 字典序升序排列
    · 排除 sign 本身、排除空值
    · app_secret 只拼在【开头】，不拼结尾
    · 计算签名时中文【不】url编码，但发请求时【要】url编码

请求方式：
    POST https://openapi.jushuitan.com<接口路径>
    Content-Type: application/x-www-form-urlencoded;charset=utf-8
    公共参数：app_key / access_token / timestamp / version=2 / charset=utf-8 / sign / biz(JSON字符串)
"""

import json
import time
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://openapi.jushuitan.com"
CONFIG_FILE = Path(__file__).parent / "config.json"

# 【重要】强制绕过系统代理，直连聚水潭。
# 你本机开着 v2rayN（127.0.0.1:10808），如果走代理，出口IP会变成境外节点，
# 而聚水潭 IP 白名单是按真实宽带出口IP校验的 —— 走代理会直接被拒。
# 直连出口IP = 118.125.65.21（四川眉山电信），白名单填这个。
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def get_public_ip() -> str:
    """查询本机直连的公网出口IP —— IP白名单就填这个"""
    try:
        return OPENER.open("https://myip.ipip.net", timeout=10).read().decode("utf-8", "ignore").strip()
    except Exception as e:
        return f"查询失败: {e}"


class JSTError(Exception):
    """聚水潭接口返回的错误"""
    pass


def get_sign(app_secret: str, data: dict) -> str:
    """计算签名：MD5(app_secret + 排序后拼接串)，32位小写"""
    sign_str = app_secret
    for key in sorted(data.keys()):
        if key == "sign":
            continue
        value = data[key]
        if value is None or value == "":
            continue
        sign_str += str(key) + str(value)
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()


class JSTClient:
    def __init__(self, app_key=None, app_secret=None, access_token=None, refresh_token=None):
        cfg = {}
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

        self.app_key = app_key or cfg.get("app_key")
        self.app_secret = app_secret or cfg.get("app_secret")
        self.access_token = access_token or cfg.get("access_token")
        self.refresh_token = refresh_token or cfg.get("refresh_token")
        self.cfg = cfg

        missing = [k for k, v in {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
        }.items() if not v or str(v).startswith("你的")]
        if missing:
            raise ValueError(f"config.json 里这些值没填：{missing}")

        # access_token 为空 → 自动获取初始token（自有商城应用随时可调，token过期后也一样）
        if not self.access_token:
            self.get_init_token()

    # ---------- 核心请求 ----------
    def request(self, api_path: str, biz: dict = None, retry_on_token_expire: bool = True) -> dict:
        """调用任意聚水潭接口。biz 为业务参数 dict，自动序列化成公共参数 biz"""
        params = {
            "app_key": self.app_key,
            "access_token": self.access_token,
            "timestamp": int(time.time()),
            "version": 2,
            "charset": "utf-8",
            "biz": json.dumps(biz or {}, ensure_ascii=False, separators=(",", ":")),
        }
        params["sign"] = get_sign(self.app_secret, params)

        body = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            BASE_URL + api_path,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            method="POST",
        )

        try:
            with OPENER.open(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise JSTError(f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')}")
        except Exception as e:
            raise JSTError(f"请求失败: {e}")

        code = result.get("code")
        # token 失效 → 先刷新，刷新不行就重新拿初始token，再重试一次
        if code != 0 and retry_on_token_expire and self._is_token_error(result):
            try:
                self.refresh_access_token()
            except JSTError:
                # token 完全过期后 refreshToken 接口也会拒绝，此时 getInitToken 重新获取
                self.get_init_token()
            return self.request(api_path, biz, retry_on_token_expire=False)
        if code != 0:
            raise JSTError(f"接口 {api_path} 返回错误 code={code}, msg={result.get('msg')}")
        return result

    @staticmethod
    def _is_token_error(result: dict) -> bool:
        msg = str(result.get("msg", ""))
        return any(k in msg for k in ("token", "Token", "TOKEN", "授权", "过期", "失效"))

    # ---------- Token 管理 ----------
    def _save_tokens(self):
        """把最新 token 回写 config.json，下次直接用"""
        if CONFIG_FILE.exists():
            self.cfg["access_token"] = self.access_token
            self.cfg["refresh_token"] = self.refresh_token
            CONFIG_FILE.write_text(
                json.dumps(self.cfg, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    def get_init_token(self) -> str:
        """获取初始 access_token（自有商城应用专用，token 过期后也可用本接口重新获取）。
        文档 docId=23：grant_type 固定 authorization_code，code 为自定义随机6位字符串。"""
        import random
        import string

        params = {
            "app_key": self.app_key,
            "timestamp": int(time.time()),
            "grant_type": "authorization_code",
            "charset": "utf-8",
            "code": "".join(random.choices(string.ascii_letters + string.digits, k=6)),
        }
        params["sign"] = get_sign(self.app_secret, params)
        body = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            BASE_URL + "/openWeb/auth/getInitToken",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            method="POST",
        )
        with OPENER.open(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("code") != 0:
            raise JSTError(f"获取初始 token 失败: code={result.get('code')}, msg={result.get('msg')}")

        data = result.get("data", {})
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token") or self.refresh_token
        self._save_tokens()
        return self.access_token

    def refresh_access_token(self) -> str:
        """用 refresh_token 续期 access_token（有效期30天），并回写 config.json"""
        if not self.refresh_token:
            raise JSTError("没有 refresh_token，无法自动续期，请去开放平台重新获取")

        params = {
            "app_key": self.app_key,
            "timestamp": int(time.time()),
            "grant_type": "refresh_token",
            "charset": "utf-8",
            "refresh_token": self.refresh_token,
            "scope": "all",
        }
        params["sign"] = get_sign(self.app_secret, params)
        body = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            BASE_URL + "/openWeb/auth/refreshToken",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            method="POST",
        )
        with OPENER.open(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("code") != 0:
            raise JSTError(f"刷新 token 失败: {result.get('msg')}")

        data = result.get("data", {})
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token") or self.refresh_token
        self._save_tokens()
        return self.access_token

    # ---------- 常用业务接口 ----------
    def get_shops(self) -> list:
        """店铺查询 /open/shops/query —— 用来做连通性测试。返回字段实际是 data.datas"""
        result = self.request("/open/shops/query", {"page_index": 1, "page_size": 100})
        data = result.get("data", {})
        return data.get("datas") or data.get("shops") or []

    def fetch_out_orders(self, start_time: str = None, end_time: str = None,
                         page_size: int = 100, max_pages: int = 500) -> list:
        """
        销售出库单查询 /open/orders/out/simple/query
        用 ts 游标翻页（官方推荐方式）：第一次 start_ts=1，之后传上一页返回的最大 ts
        start_time / end_time 格式 'YYYY-MM-DD HH:MM:SS'，传了则在本地按时间过滤
        """
        all_orders, start_ts, seen_ts = [], 1, set()

        for _ in range(max_pages):
            biz = {"start_ts": start_ts, "is_get_total": False,
                   "page_index": 1, "page_size": page_size}
            result = self.request("/open/orders/out/simple/query", biz)
            orders = result.get("data", {}).get("orders", []) or []
            if not orders:
                break

            for o in orders:
                ts = o.get("ts")
                if ts is None:
                    continue
                if ts in seen_ts:      # 去重，防止游标不前进导致死循环
                    continue
                seen_ts.add(ts)
                all_orders.append(o)

            max_ts = max(o["ts"] for o in orders if o.get("ts") is not None)
            if max_ts <= start_ts:
                break
            start_ts = max_ts

            if len(orders) < page_size:
                break

        # 本地时间过滤（避免不同接口时间字段口径不一致）
        if start_time or end_time:
            filtered = []
            for o in all_orders:
                t = o.get("modified") or o.get("created") or ""
                if start_time and t < start_time:
                    continue
                if end_time and t > end_time:
                    continue
                filtered.append(o)
            return filtered
        return all_orders

    # ---------- 分⻚拉取通用逻辑（按 page_index 翻页的接口） ----------
    def _fetch_paged(self, api_path: str, data_key: str, biz_base: dict = None,
                     page_size: int = 50, max_pages: int = 200) -> list:
        """
        通用分页拉取。data_key 是返回结构里列表所在的字段名（如 orders / inventorys / refunds）。
        首次调用后会自动探测真实字段名，探测不到就把整个 data 当成一条返回，不会静默丢数据。
        """
        all_rows = []
        for page in range(1, max_pages + 1):
            biz = dict(biz_base or {})
            biz["page_index"] = page
            biz["page_size"] = page_size
            result = self.request(api_path, biz)
            data = result.get("data", {}) or {}

            rows = data.get(data_key)
            if rows is None:
                # 字段名猜错了 → 自动探测第一个 list 字段
                for k, v in data.items():
                    if isinstance(v, list):
                        rows, data_key = v, k
                        break
            if rows is None:
                if page == 1 and data:
                    all_rows.append(data)   # 单条对象型返回
                break
            if not rows:
                break

            all_rows.extend(rows)
            if len(rows) < page_size:
                break
        return all_rows

    def fetch_orders(self, start_time: str = None, end_time: str = None, **extra) -> list:
        """订单查询 /open/orders/single/query —— 非淘系订单，含未发货/异常状态"""
        biz = dict(extra)
        if start_time:
            biz["start_time"] = start_time
        if end_time:
            biz["end_time"] = end_time
        return self._fetch_paged("/open/orders/single/query", "orders", biz)

    def fetch_inventory(self, **extra) -> list:
        """商品库存查询 /open/inventory/query"""
        return self._fetch_paged("/open/inventory/query", "inventorys", dict(extra), page_size=100)

    def fetch_refunds(self, start_time: str = None, end_time: str = None, **extra) -> list:
        """售后退货退款查询 /open/refund/single/query"""
        biz = dict(extra)
        if start_time:
            biz["start_time"] = start_time
        if end_time:
            biz["end_time"] = end_time
        return self._fetch_paged("/open/refund/single/query", "refunds", biz)


# ---------- 工具：拉平存 CSV ----------
def save_flat_csv(rows: list, out_path, items_key: str = None):
    """把嵌套 JSON 摊平成 CSV（动态列，不用猜字段）。
    items_key 不为空时，按明细行展开（一行一个商品）。"""
    import csv

    def flatten(obj, prefix=""):
        flat = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                flat.update(flatten(v, f"{prefix}{k}_"))
        elif isinstance(obj, list):
            flat[prefix.rstrip("_")] = json.dumps(obj, ensure_ascii=False)
        else:
            flat[prefix.rstrip("_")] = obj
        return flat

    out_rows = []
    for r in rows:
        base = flatten(r)
        if items_key and isinstance(r.get(items_key), list) and r[items_key]:
            for item in r[items_key]:
                merged = dict(base)
                merged.update(flatten(item, "item_"))
                out_rows.append(merged)
        else:
            out_rows.append(base)

    if not out_rows:
        print("没有数据可写")
        return 0

    cols = []
    for r in out_rows:
        for k in r.keys():
            if k not in cols:
                cols.append(k)

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    print(f"已写出 {len(out_rows)} 行 → {out_path}")
    return len(out_rows)
