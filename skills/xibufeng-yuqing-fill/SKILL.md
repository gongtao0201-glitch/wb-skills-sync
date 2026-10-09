---
name: xibufeng-yuqing-fill
description: 西部风舆情监测台账自动填报。当用户说"填台账""补台账""查抖音视频填进去""舆情监测"等时使用。能力：连接 WPS 云文档定位台账 → 用蝉妈妈检索真实可打开的抖音视频 → 按四维评分标准自动评级 → 安全写入在线协作表格（只写空格、绝不覆盖他人内容）→ 逐格回读验证 + 逐条验证链接可打开。
agent_created: true
---

# 西部风舆情监测台账自动填报

## 何时使用

用户要求填写「公关舆论小组舆情监测台账」（WPS 在线表格），包括：补填空缺列、追加新条目、
按规则重算评分、查询真实抖音视频并登记。

## 铁律（违反会造成事故）

1. **绝不覆盖他人已填内容** —— 这是多人实时协作的在线表。任何写入前必须基于当次快照判空，
   只写 `(cellText || '').trim() === ''` 的格子。
2. **表在实时变化** —— 实测同一轮内 rowTo 从 178→179→180→182。**每次写入前必须重新读取**，
   禁止复用上一轮的快照，否则会覆盖别人刚写的行。
3. **写完必须独立回读逐格比对**，不能只信 `code: 0`。
4. **链接必须验证可打开**（curl HTTP 200）后才写入，禁止编造链接。
5. 复核(11) / 实际处置(13) / 是否申报奖励(14) / 处置(15) 属组长环节，**默认不代填**。

## 环境准备

### WPS 云文档 CLI

```bash
export PATH="/usr/bin:/bin:$PATH"   # 本机 bash PATH 是坏的，必须先修
KD="C:/Users/Administrator/AppData/Local/kdocs-cli/kdocs-cli.exe"
```
- 未安装：`cd ~/.workbuddy/skills/kdocs && node scripts/setup.cjs`
- 未登录：`kdocs-cli auth login`（浏览器 OAuth，Token 存密钥链，约 1 年有效）
  - ⚠️ `auth login --help` **也会真的触发登录流程**，别随手敲
- 401 = Token 过期 → 重新 `auth login`

### 参数命名两套，别混

| 操作 | CLI action | 参数风格 |
|---|---|---|
| 读 | `sheet get-range-data` | 驼峰：`sheetId` + `range{rowFrom,rowTo,colFrom,colTo}` |
| 写 | `sheet range-data-batch-update` | 下划线：`worksheet_id` + `range_data[]{op_type,row_from,row_to,col_from,col_to,formula}` |

`op_type` 固定 `cell_operation_type_formula`（写文本也用它）。
中文/长参数一律写 JSON 文件用 `--file` 传，禁止 key=value（Windows 破坏 UTF-8）。

### 蝉妈妈（查真实抖音视频）

`CMM_API_KEY` 已配置在环境变量。权限检查：
```
GET https://ai-api.chanmama.com/v1/cmm/api/permission/list?intent=<描述>
Authorization: Bearer $CMM_API_KEY
```

## 台账结构

`file_id: ALA42NLnmxM6RVRxbKHRxxjeeenW2v7z1`（9月台账，每月可能换，先搜索确认）

| sheetId | 名称 | 用途 |
|---|---|---|
| 1 | 舆情监测台账 | 主表，填写目标 |
| 3 | 四维评分标准 | 规则表（评分前必读） |
| 5 | 评论话术库 | 话术素材 |

主表 16 列（0-based），表头 R1+R2 合并，R3 是填写说明，**数据区从 R4 起**：

```
0序号 1登记日期 2内容日期 3平台 4链接 5内容摘要 6涉及产品
7性质(正/负) 8初判等级 9四维评分 10责任人 11复核情况 12发布人
13实际处置 14是否申报奖励 15处置
```

## 四维评分规则（表2）—— ⚠ 2026-09-22 已修订，旧分级作废

**每次填报前必须重读 sheetId=3 的 R0–R33**，规则改过一版，别用记忆里的旧值。

- **负面四维**：影响范围 / 传播速度 / 法律风险 / 品牌关联度
- **正面四维**：品牌影响力 / 传播潜力 / 可信合规度 / 品牌关联度
- 每维 1–5 分。**现行分级（修订版）：4–9 四级 ｜ 10–14 三级 ｜ 15–17 二级 ｜ 18–20 一级**
  （旧版是 4–7/8–11/12–15/16–20，**已作废**）

**各维 1/3/5 档判定（正面）**
| 维度 | 1 分 | 3 分 | 5 分 |
|---|---|---|---|
| 品牌影响力 | 单平台单条，价值有限 | 多平台多条 / 进入话题页 | 热搜 / 主流媒体 / 权威 KOL |
| 传播潜力 | 增速平缓、无裂变 | 当日明显增长、有互动 | 小时级指数扩散、被二次传播 |
| 可信合规度 | 可信度低 / 表述存疑 | 基本可验证、合规 | 有实测/钓获实景/数据或权威背书 |
| 品牌关联度 | 弱关联 / 行业话题 | 直接涉及我司产品 | 核心产品 / 主力品牌正面点名 |

**触发与封顶（新增，必须检查）**
- 一级 ≥18 且 品牌影响力≥4 且 可信合规度≥4
- 二级 ≥15 且 可信合规度≥3 且 品牌关联度≥3，缺一项降为三级
- 封顶：可信合规度=1 → 封顶三级；品牌关联度≤2 → 封顶三级
- 容量：一级+二级 每周 1–2 条为正常水位，**不必凑数**，大部分素材是三级

**正面内容禁止使用负面维度名**（现有表里有多处填错，可作为对照参考）

**链接列格式**：表内主流是抖音 app 复制的分享文案
（`3.58 复制打开抖音，看看【xxx的作品】标题… https://v.douyin.com/xxx/`）。
AI 拿不到这种短链，**禁止伪造**；统一填 `https://www.douyin.com/video/{aweme_id}` 并验证 200。
已填过的条目组长复核时可能标「链接失效」，属内容下架，非格式问题。

## 填报流程

### 1. 定位与探测
```bash
$KD drive list-latest-items --silent      # 找 file_id（搜"舆情监测台账"）
$KD sheet get-sheets-info '{"file_id":"<FID>"}' --silent
```

### 2. 实时全量读取
先 `get-sheets-info` 拿 `rowTo`（**会变**：实测 178→179→180→182→**365**），再读
`range{rowFrom:0,rowTo:<rowTo>,colFrom:0,colTo:15}`，记录：
- 最后有内容的行 `maxR`（决定空白区起点）
- 当前最大序号 `maxSeq`

⚠️ 表会被重排：已填行的**序号会变**（我 9/11 填的 173–180，9/22 再看已变成 177–184），
所以事后核查要按「链接/发布人」定位，不要按序号。
⚠️ 尾部常有**只填了序号的预置空行**（如 R335–R365 序号 324–354），直接接着填即可，
不要再跳 2 行间隔，否则序号与预置骨架错位。

### 3. 检索真实抖音视频（蝉妈妈）

```json
{"api":"video_library_custom_search_video",
 "query":{"keyword":"西部风窝料","create_start_time":"2026-08-26","create_end_time":"2026-09-11","sort":"digg_count","page":1}}
```
```bash
curl -s -X POST https://ai-api.chanmama.com/v1/cmm/api/execute \
  -H "Authorization: Bearer $CMM_API_KEY" -H "Content-Type: application/json" \
  --data-binary @q.json
```

返回 `data.data.list[]`，每条结构：
- `视频信息.抖音播放地址` → 正则 `slides\/(\d+)|\/video\/(\d+)` 提取 19 位 aweme_id
- `视频信息.{视频标题,视频发布时间,点赞数,评论数}`、`达人信息.达人名称`
- 构造标准链接：`https://www.douyin.com/video/{aweme_id}`

**⚠️ 关键词陷阱**：搜「西部风」会命中「西部风长靴」等服装内容。用
`西部风窝料 / 西部风A30 / 西部风A35 / 西部风酒米 / 西部风新品 / 西部风颗粒 / 打窝颗粒A30 / 老坛甜薯`，
再用 `/西部风/i.test(title)` 二次过滤。仅含「老坛甜薯」等通用词的多是竞品，需人工判品牌。

**链接验证**（必须做）：
```bash
curl -s -o /dev/null -w "%{http_code}" -L --max-time 25 \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36" \
  "https://www.douyin.com/video/<aweme_id>"
```
返回 200 才算可打开。
⚠️ 用 bash 跑 curl；node 的 `execFileSync` 下 `-o /dev/null` 会失败（报 ERR，是调用方式问题不是链接问题）。

### 4. 生成待填 ops（严格判空）

对每列：只有当 `V(r,c)` 为空时才加入 ops。跳过完全空行（残行不编号）。
- 平台(3)：链接含 `douyin/抖音`→抖音，`kuaishou/快手`→快手
- 发布人(12)：从标题/链接正则 `【(.+?)的(?:图文)?作品】` 或取达人名称
- 登记日期(1)：仅当上下行日期相同时才补（否则宁可空着）
- 内容日期(2)：视频发布日期，`2026-09-01` → `2026.9.01`
- 时间约束：**登记日期与内容日期相差不超过 16 天**（爆款点赞10万+ 不受限）

### 5. 写入

从空白区起点写（有预置序号则对齐序号，无则 maxR+3 留 2 行间隔给同时在线的同事）。
`range_data` 每批 22 格较稳，批间 sleep 1.5s 防限频（429001/429002 时需停到恢复时间）。

**去重必做**：表内已有 300+ 条，按 ID 去重基本无效（链接列是分享文案，不含完整 aweme_id），
要靠**摘要前 24 字（去 #/@/空格）**比对 + 品牌词过滤。关键词命中后先过滤再挑。

### 6. 验证

- 重读目标区，逐格与 ops 比对，输出 `成功 N/M`
- 逐条 curl 验证链接 HTTP 200
- 检查序号连续性有无重复

## 本机环境坑

1. **bash PATH 坏**：任何 bash 命令首行加 `export PATH="/usr/bin:/bin:$PATH"`
2. **PowerShell 工具不回显 stdout**，且疑似未真正执行 → 排查/验证一律走 bash
3. `reg.exe` 被安全策略黑名单拦截
4. `/tmp` 在 bash 里会被解析成 `D:\tmp` → 临时文件放工作区 `.workbuddy/tmp/`

## 已知遗留

- 序号 172 在 R179/R180 重复（我写 R179 后同事新增 R180 照抄同号），Yan 决定先不动
- G 列（涉及产品）有 63 行是 DISPIMG 图片公式（截图），无法文本分析
- 2026-09-11 我填的 8 条位于 R182–R189（现序号 177–184，责任人龚涛），其中 R188 被标「链接失效」
- 2026-09-22 又填 8 条，位于 **R335–R342（序号 324–331）**，全部三级，88 格回读一致、链接 8/8 可打开

## 本机环境坑（补充）

5. **kdocs-cli 升级提示会污染 stdout**：有新版时 CLI 会在 JSON 前插一行
   `⚠ kdocs-cli vX available`，导致 `JSON.parse` 失败 → 先 `kdocs-cli upgrade -y` 再解析
6. **node 脚本 `process.argv`**：`argv[1]` 是脚本自身路径，**第一个参数从 `argv[2]` 开始**
7. `sheet get-range-data` 的 `sheetId` 要传内部 ID（1/3/5），**不是** `sheetIdx`（0/1/2）
8. 成功响应体是 `{result:"ok"}`，没有 `code` 字段；判断成功用 `d.result === 'ok'`
