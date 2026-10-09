---
name: xibufeng-jst-query
description: 查询西部风公司聚水潭 ERP 的经营数据——销售排行、分平台表现、库存水位、退货分析、商品成本价与毛利率。当用户问"哪个品卖得好""卖了多少""库存够不够""退货多不多""各平台/店铺表现""毛利率""某个商品的销量"等与西部风销售、库存、售后相关的问题时使用本技能。
---

# 西部风聚水潭数据查询

从公司聚水潭 ERP 拉取真实经营数据。**数据来自公司系统，不要编造任何数字**——查不到就如实说查不到，并按下面的错误处理提示用户。

## 🔗 共享数据（2026-09-11 加装，与 Codex 共用）

WorkBuddy 与 Codex 读**同一个 SQLite**，不存在两份数据对不上的问题：

| 项目 | 路径 |
|------|------|
| 共享数据根 | `C:\Users\Administrator\AI共享数据` |
| 数据源索引 | `C:\Users\Administrator\AI共享数据\数据源索引.json` |
| 统一入口 | `C:\Users\Administrator\AI共享数据\共享查询.py` |

```bash
python "C:\Users\Administrator\AI共享数据\共享查询.py" status     # 数据新不新，一眼看清
python "C:\Users\Administrator\AI共享数据\共享查询.py" jst summary --days 7
```

## ⭐ 首选方案：查本地 SQLite（秒级响应，用户明确要求）

**不要每次分析都去调聚水潭 API** —— 这是用户定下的铁律（Yan 原话："千万不可以每次都去调用聚水潭的接口"）。
历史数据已经全量落到本地，**任何分析类问题一律查本地库**：

| 项目 | 值 |
|------|-----|
| 本地数据库 | `C:\Users\Administrator\Desktop\聚水潭ai\data\jst_sales.db` |
| 覆盖范围 | 2026-04-01 起至今的全量出库单（170 万+ 单，600MB+） |
| 秒查脚本 | `python local_query.py status` / `by-category` / `by-shop` 等 |
| 周报 | `python weekly_summary.py`（默认上周，约 2 秒） |
| 月报 | `python monthly_summary.py --month 2026-08`（约 2 秒） |
| 拉新数据 | `python daily_sync.py --yesterday`（拉昨天，5-8 分钟） |

表结构：`order_headers`(io_id, io_date, shop_id, shop_name, status, logistics_*, modified)、
`order_items`(io_id, sku_id, pic_name, spec_name, qty, src_price, src_price_total,
seller_income_amount, buyer_paid_amount, pic_cost)、`products`(pic_name, category)。

⚠️ **金额字段**：出库单 `src_price` 恒为 0，**必须用 `seller_income_amount`**。

### 何时才调 API
只有在本地数据不新（DB 最新日期 < 昨天）时才同步一次，然后立刻回到本地查询。

### 同步精度：实测结论（2026-09-07），别再过度设计

对同一发货日用三档窗口实测：次日凌晨口径 13,499 单 → 放宽到 D+2 得 13,513（**+0.10%**）→ 放宽到 D+6 仍是 13,513（**已收敛**）。

> **次日凌晨拉昨天就够了，捕获率 99.9%。不需要每周/每月全量重拉。**

同步侧踩过的坑（不一定都会再犯，但要知道症状）：
1. `page_size` 实际最大 100，传 500 也只返 100 条
2. 单次查询绝对不能超 **780 页**（第 801 页必报假「频次超限」，重试无用）→ `daily_sync.py` 已改为**逐日拉取**
3. 旧版一次性拉多天会触发页数上限，接口按 modified **升序**返回 → 后面的日期**静默丢失**
4. **真正的风险是「整天没拉到」**（电脑关机、进程被杀），不是滞后单
   → 用 `python 补齐缺口日.py --start <起始日> --end <结束日>` 做缺口自检（低于同月中位数 30% 判定），
   月底出报表前用 `--threshold 0.70` 做严格体检
5. 某天数字看着少，**先确认是不是拉取当天还没过完**（当天中午拉的只有半天数据）

### ⚠️ 口径差异（业务沟通必知）

我方库里的单数**比聚水潭后台的出库单数少约 5%**，这是正常的：
- `status = Delete` 的**作废/取消单不入表**（实测 9/5：接口 13,513 → 库存 12,812，差值全是作废单）
- 纯赠品单没有 sku，也不计入销售
- 统计金额一律用 **`seller_income_amount`**（出库单 `src_price` 恒为 0）

## 备用方案：实时调接口（仅限本地没覆盖的需求，如库存/退货）

## 执行方式

本技能目录下的 `query.py` 是统一入口。执行前先确认 Python 可用：

```bash
python --version
```

如果提示找不到 python，依次尝试：

```bash
py --version
"%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" --version
```

找到可用的那个命令后，用它执行（下文用 `python` 代称，替换成实际可用的命令）。
包内零第三方依赖，**不要** pip install 任何东西。

工作目录必须切到本技能所在目录，例如：

```bash
cd "C:\Users\<用户名>\.workbuddy\skills\xibufeng-jst-query"
python query.py shop-list
```

## 命令对照表

| 用户想问什么 | 执行什么 |
|-------------|---------|
| 有哪些店铺/平台 | `python query.py shop-list` |
| 哪个品卖得好、销量排行、卖了多少钱 | `python query.py sales --days 30 --top 10` |
| 各平台/各店铺表现对比 | `python query.py shop --days 30` |
| 退货情况、哪些品退货多 | `python query.py refund --days 30` |
| 库存、哪些品缺货 | `python query.py inventory` |
| 商品档案、成本价、毛利率 | `python query.py item --keyword 窝料` |
| 接口能不能用（排障第一步） | `python query.py diagnose` |

参数：
- `--days N`：统计最近 N 天，默认 30
- `--top N`：前 N 名，默认 10
- `--keyword 关键词`：按商品名称筛选（item 命令用）
- `--json`：输出原始 JSON（需要进一步处理时用）

## 输出与解读

脚本输出的是**真实数据**。拿到后：
- 按用户的问题组织成结论，不要罗列原始 JSON
- 金额单位是元，涉及金额用 ¥ 符号
- 商品分类（窝料/饵料/小药/配件）属于业务判断，**不要替用户猜**，需要分类时直接问用户

## 错误处理（重要）

| 报错 | 含义 | 怎么处理 |
|------|------|---------|
| `接口「XXX」还没有申请权限` | 该接口公司没开通 | 告诉用户去聚水潭开放平台申请，并转述脚本给出的具体路径（哪个目录、哪个接口名） |
| `验证失败！无API权限` | 同上 | 同上 |
| `IP 不在白名单` / 连接超时 | 公司网络出口 IP 变了 | 让用户跑 `python check_ip.py` 拿到新 IP，去开放平台应用后台更新 IP 白名单 |
| `token` 相关错误 | 访问令牌问题 | 脚本会自动重取，重试一次；仍失败则让用户找管理员（严过关） |
| 查不到数据 | 区间内确实没有单据 | 如实告诉用户，可建议换个时间区间重试 |

排障第一步永远是先跑 `python query.py diagnose`，它会列出哪些接口能用、哪些不能。

## 注意事项

- **绝不编造数据**。查不到就说查不到。
- 不要直接把 `config.json` 里的密钥内容展示给用户或写进任何输出。
- 单次查询数据量较大时，脚本可能返回原始 JSON 摘要；需要完整分析时加 `--json` 再自行处理。
