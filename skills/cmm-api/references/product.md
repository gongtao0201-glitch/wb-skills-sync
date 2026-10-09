# 商品 API 参考

仅当用户的 CMM 请求主要属于该实体领域时使用此文件。

## 分类默认查询字段

适用时使用该分类的默认查询字段。

## API 索引

| API | 摘要 |
| --- | --- |
| product_library_custom_search_product | 通过商品属性/商品标题关键字、商品基础信息和商品关键数据指标多条件组合，筛选出满足条件的商品列表，支持按指定指标排序。列表信息包括：商品标题、商品头图、商品价格、商品数据指标、商品近30天销量趋势。 |
| product_basic_info | 获取指定商品的基础信息。 |
| product_audience_profile | 获取指定商品的观众画像（性别年龄地区） |
| product_order_profile | 获取指定商品的成交画像（性别年龄地区） |
| product_comments | 获取指定商品的评价列表，按点赞数倒叙，信息包含：商品评价原文、评价时间、评价点赞数 |
| product_key_metrics_live_video_author_sales_data_daily_detail | 获取指定商品在周期内的关键数据指标明细，按日返回各数据指标值，包括：商品数据、销售数据、关联直播数据、关联视频数据、关联达人数据。 |
| product_related_commerce_author_list | 获取指定商品在周期内关联的带货达人列表，列表信息包含：达人基础信息、该达人在商品上产生的销售数据（如：销量、销售额、关联直播数、关联视频数等）。 |
| product_related_commerce_live_list | 获取指定商品在周期内关联的带货直播列表，列表信息包括：直播基础信息、商品在该直播间的销售数据。 |
| product_related_commerce_video_list | 获取指定商品在周期内关联的带货视频列表，列表信息包括：视频基础信息、商品在该视频产生的销售数据。 |
| product_top_selling_product_rank_period | 获取历史周期的商品热销榜单，榜单按周期内商品销量降序取TOP商品列表，列表信息包括：商品基础信息、销售数据、近30天销量趋势。 |
| product_hot_promotion_product_rank_period | 获取历史周期的商品热推榜单，榜单按周期内商品关联带货达人数降序取TOP商品列表，列表信息包括：商品基础信息、关联达人数据、销售数据、近30天销量趋势。 |
| product_top_selling_live_product_rank_period | 获取历史周期的直播商品热销榜单，榜单按周期内商品直播销量降序取TOP商品列表，列表信息包括：商品基础信息、销售数据、近30天直播销量趋势。 |
| product_top_selling_video_product_rank_period | 获取历史周期的视频商品热销榜单，榜单按周期内商品视频销量降序取TOP商品列表，列表信息包括：商品基础信息、销售数据、近30天视频销量趋势。 |
| product_key_metrics_live_video_author_sales_data_period_total | 获取指定商品在周期内的关键数据指标，返回周期内各指标的合计值，包括：商品数据、销售数据、关联直播数据、关联视频数据、关联达人数据。 |
## API 详情

### product_library_custom_search_product

- 摘要：通过商品属性/商品标题关键字、商品基础信息和商品关键数据指标多条件组合，筛选出满足条件的商品列表，支持按指定指标排序。列表信息包括：商品标题、商品头图、商品价格、商品数据指标、商品近30天销量趋势。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | 否 | 商品属性/商品标题关键字（示例：面包、洗面奶），非必填 |
| multi_category_id | 否 | 商品分类ID/商品品类名称，可多选（多选用逗号分隔），非必填 |
| day_type | 否 | 可选查询周期：1（昨天）、7（近7天）、30（近30天），非必填 |
| price | 否 | 商品价格区间，格式最小值-最大值（如0-1000），非必填 |
| mulit_commission_rate | 否 | 精选联盟佣金比例区间，单位百分比，格式最小值-最大值（如10-20、10-)，非必填 |
| duration_volume | 否 | 周期内销量区间，格式最小值-最大值（如0-1000），非必填 |
| duration_author_count | 否 | 周期内关联达人数，格式最小值-最大值（如100-200、100-)，非必填 |
| most_volume | 否 | 销售方式：1（视频带货为主）、2（直播带货为主）、3（商品卡带货为主），非必填 |
| channel | 否 | 带货渠道：1（达人号为主）、2（品牌自营号为主）、3（商家自营号为主），非必填 |
| is_new_product | 否 | 填1筛选周期内新上架商品，非必填 |
| fans_gender | 否 | 观众画像性别：-1（不限）、0（粉丝男性居多）、1（粉丝女性居多），非必填 |
| fans_age | 否 | 观众画像年龄区间，1（18-23岁）、2（24-30岁）、3（31-40岁）、4（41-50岁）、5（50岁以上），单选，非必填 |
| fans_province | 否 | 观众画像省份，如：福建省，仅支持单个省份，非必填 |
| order_gender | 否 | 成交画像性别，1（男性成交居多）、2（女性成交居多），非必填 |
| order_age | 否 | 成交画像年龄区间，1（18-23岁）、2（24-30岁）、3（31-40岁）、4（41-50岁）、5（50岁以上），单选，非必填 |
| sort | 否 | 排序字段：duration_volume（销量）、duration_amount（销售额）、duration_live_volume（直播销量）、duration_live_amount（直播销售额）、duration_aweme_volume（视频销量）、duration_aweme_amount（视频销售额）、duration_other_amount（商品卡销售额）、duration_other_volume（商品卡销量）、duration_author_count（关联达人数），history_total_volume（近一年销量）、history_total_amount（近一年销售额）、duration_product_rate（近30天转化率）、duration_aweme_count（关联视频数）、duration_live_count（关联直播数），非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| 1 | 昨天 |
| 7 | 近7天 |
| 30 | 近30天 |

`most_volume`:

| 取值 | 含义 |
| --- | --- |
| -1 | 不限 |
| 1 | 视频带货为主 |
| 2 | 直播带货为主 |
| 3 | 商品卡带货为主 |

`channel`:

| 取值 | 含义 |
| --- | --- |
| -1 | 不限 |
| 1 | 达人号为主 |
| 2 | 品牌自营号为主 |
| 3 | 商家自营号为主 |

`is_new_product`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新上架商品 |

`fans_gender`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 观众画像-男性居多 |
| 2 | 观众画像-女性居多 |

`fans_age`:

| 取值 | 含义 |
| --- | --- |
| 1 | 18-23岁 |
| 2 | 24-30岁 |
| 3 | 31-40岁 |
| 4 | 41-50岁 |
| 5 | 50岁以上 |

`order_gender`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 成交画像-男性居多 |
| 2 | 成交画像-女性居多 |

`order_age`:

| 取值 | 含义 |
| --- | --- |
| 1 | 18-23岁 |
| 2 | 24-30岁 |
| 3 | 31-40岁 |
| 4 | 41-50岁 |
| 5 | 50岁以上 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| mulit_commission_rate | 佣金比例 |
| duration_volume | 周期销量 |
| duration_live_volume | 周期直播销量 |
| duration_aweme_volume | 周期视频销量 |
| duration_other_volume | 周期商品卡销量 |
| duration_author_count | 关联达人数 |
| duration_live_count | 关联直播数 |
| duration_amount | 周期销售额 |
| duration_live_amount | 周期直播销售额 |
| duration_aweme_amount | 周期视频销售额 |
| duration_other_amount | 周期商品卡销售额 |
| history_total_volume | 近一年销量 |
| history_total_amount | 近一年销售额 |
| duration_aweme_count | 关联视频数 |
| duration_pv | 周期内浏览量 |
| duration_product_rate | 周期内转化率 |

示例:

```json
{}
```

### product_basic_info

- 摘要：获取指定商品的基础信息。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| promotion_id | 是 | 指定单个商品ID/商品标题，必填 |

示例:

```json
{
  "promotion_id": "MwCTZlE4KEmAscYpIAJ4m-i95FX0NkCN"
}
```

### product_audience_profile

- 摘要：获取指定商品的观众画像（性别年龄地区）

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| promotion_id | 是 | 指定单个商品ID/商品标题，必填 |

示例:

```json
{
  "promotion_id": "MwCTZlE4KEmAscYpIAJ4m-i95FX0NkCN"
}
```

### product_order_profile

- 摘要：获取指定商品的成交画像（性别年龄地区）

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| product_id | 是 | 指定单个商品ID/商品标题，必填 |

示例:

```json
{
  "product_id": "FfxtFKtx2dGKZwPbMtC5X9Zbf2mG4dnt"
}
```

### product_comments

- 摘要：获取指定商品的评价列表，按点赞数倒叙，信息包含：商品评价原文、评价时间、评价点赞数

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| promotion_id | 是 | 指定单个商品ID/商品标题，必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

示例:

```json
{
  "promotion_id": "qyS9cQFyonC-sg-ETKbtGeTQtPU_scep"
}
```

### product_key_metrics_live_video_author_sales_data_daily_detail

- 摘要：获取指定商品在周期内的关键数据指标明细，按日返回各数据指标值，包括：商品数据、销售数据、关联直播数据、关联视频数据、关联达人数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| promotion_id | 是 | 指定单个商品ID/商品标题，必填 |
| start_date | 是 | 开始时间，必填 |
| end_date | 是 | 结束时间，必填 |
| page | 否 | 页码，默认为第1页（每页返回31条），非必填 |

示例:

```json
{
  "promotion_id": "FfxtFKtx2dGKZwPbMtC5X9Zbf2mG4dnt",
  "start_date": "2025-01-25",
  "end_date": "2025-02-23"
}
```

### product_related_commerce_author_list

- 摘要：获取指定商品在周期内关联的带货达人列表，列表信息包含：达人基础信息、该达人在商品上产生的销售数据（如：销量、销售额、关联直播数、关联视频数等）。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| product_id | 是 | 指定单个商品ID/商品标题，必填 |
| start_date | 是 | 开始时间，必填 |
| end_date | 是 | 结束时间，必填 |
| is_new_corp | 否 | 填1筛选出新合作达人，非必填 |
| author_play | 否 | 填1筛选出达人号达人，非必填 |
| self_play | 否 | 填1筛选出品牌自营号达人，非必填 |
| shop_play | 否 | 填1筛选出商家自营号达人，非必填 |
| take_product_method | 否 | 筛选销售方式：1（视频带货为主）、2（直播带货为主），非必填 |
| follower_count | 否 | 粉丝数区间，格式最小值-最大值（如0-1000），非必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、follower_count（粉丝数）、room_count（关联带货直播数）、aweme_count（关联带货视频数），非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`is_new_corp`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选周期内新合作达人 |

`author_play`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选达人号 |

`self_play`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选品牌自营号 |

`shop_play`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选商家自营号 |

`take_product_method`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 视频带货为主 |
| 2 | 直播带货为主 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| amount | 销售额 |
| volume | 销量 |
| follower_count | 粉丝数 |
| reputation | 达人带货口碑 |
| room_count | 关联带货直播数 |
| aweme_count | 关联带货视频数 |

示例:

```json
{
  "product_id": "FfxtFKtx2dGKZwPbMtC5X9Zbf2mG4dnt",
  "start_date": "2025-01-25",
  "end_date": "2025-02-23"
}
```

### product_related_commerce_live_list

- 摘要：获取指定商品在周期内关联的带货直播列表，列表信息包括：直播基础信息、商品在该直播间的销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| product_id | 是 | 指定单个商品ID/商品标题，必填 |
| start_date | 是 | 开始时间，必填 |
| end_date | 是 | 结束时间，必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、begin_time（开播时间），非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`sort`:

| 取值 | 含义 |
| --- | --- |
| volume | 销量 |
| begin_time | 开播时间 |
| amount | 销售额 |

示例:

```json
{
  "product_id": "FfxtFKtx2dGKZwPbMtC5X9Zbf2mG4dnt",
  "start_date": "2025-01-25",
  "end_date": "2025-02-23"
}
```

### product_related_commerce_video_list

- 摘要：获取指定商品在周期内关联的带货视频列表，列表信息包括：视频基础信息、商品在该视频产生的销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| promotion_id | 是 | 指定单个商品ID/商品标题，必填 |
| start_date | 是 | 开始时间，必填 |
| end_date | 是 | 结束时间，必填 |
| is_new_corp | 否 | 填1筛选出周期内新发布视频，非必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、aweme_digg_count（点赞数）、aweme_comment_count（评论数）、aweme_share_count（转发数）、aweme_careate_time（发布时间），非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`is_new_corp`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选周期内新发布视频 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| aweme_careate_time | 发布时间 |
| volume | 本品销量 |
| amount | 本品销售额 |
| aweme_digg_count | 点赞数 |
| aweme_comment_count | 评论数 |
| aweme_share_count | 转发数 |

示例:

```json
{
  "promotion_id": "m6sQBHltFJ6Y526IOFccPeP4Ct0v0RXQ",
  "start_date": "2025-02-17",
  "end_date": "2025-03-18"
}
```

### product_top_selling_product_rank_period

- 摘要：获取历史周期的商品热销榜单，榜单按周期内商品销量降序取TOP商品列表，列表信息包括：商品基础信息、销售数据、近30天销量趋势。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| day_type | 是 | 榜单周期类型：day（日榜）、week（周榜/大促周期）、month（月榜）、season （季度榜）、half_year（半年榜）、year（年榜），必填 |
| day | 是 | 榜单周期，示例：2025-02-23（日榜周期），20250217-20250223（周榜周期）、202501（月榜周期），202601-202612（季度/半年/年周期），20260515-20260618（大促周期，确保数据查询范围与【蝉妈妈大促数据周期】一致），必填 |
| big_promotion | 否 | 填1表示week为大促周期，只支持系统提供【蝉妈妈大促数据周期】，其余大促请勿使用大促周期查询。非必填 |
| category_id | 否 | 商品分类ID/商品分类名称(示例：食品饮料、护肤品），非必填 |
| is_new_product | 否 | 填1筛选周期内新上架商品，非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| day | 日榜 |
| week | 周榜 |
| month | 月榜 |
| year | 年榜 |
| season | 季榜 |
| half_year | 半年榜 |

`is_new_product`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新上架商品 |

示例:

```json
{
  "day_type": "day",
  "day": "2025-02-23（日榜周期"
}
```

### product_hot_promotion_product_rank_period

- 摘要：获取历史周期的商品热推榜单，榜单按周期内商品关联带货达人数降序取TOP商品列表，列表信息包括：商品基础信息、关联达人数据、销售数据、近30天销量趋势。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| day_type | 是 | 榜单周期类型：day（日榜）、week（周榜）、month（月榜），必填 |
| date | 是 | 榜单周期，示例：2025-02-23（日榜周期），20250217-20250223（周榜周期）、202501（月榜周期），必填 |
| category_id | 否 | 商品分类ID/商品分类名称(示例：食品饮料、护肤品），非必填 |
| is_new_product | 否 | 填1筛选周期内新上架商品，非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| day | 日榜 |
| week | 周榜 |
| month | 月榜 |

`is_new_product`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新上架商品 |

示例:

```json
{
  "date": "2025-02-23",
  "day_type": "day"
}
```

### product_top_selling_live_product_rank_period

- 摘要：获取历史周期的直播商品热销榜单，榜单按周期内商品直播销量降序取TOP商品列表，列表信息包括：商品基础信息、销售数据、近30天直播销量趋势。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| day_type | 是 | 榜单周期类型：day（日榜）、week（周榜）、month（月榜），必填 |
| day | 是 | 榜单周期，示例：2025-02-23（日榜周期），20250217-20250223（周榜周期）、202501（月榜周期），必填 |
| category_id | 否 | 商品分类ID/商品分类名称(示例：食品饮料、护肤品），非必填 |
| is_new_product | 否 | 填1筛选周期内新上架商品，非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| day | 日榜 |
| week | 周榜 |
| month | 月榜 |

`is_new_product`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新上架商品 |

示例:

```json
{
  "day": "2025-02-23",
  "day_type": "day"
}
```

### product_top_selling_video_product_rank_period

- 摘要：获取历史周期的视频商品热销榜单，榜单按周期内商品视频销量降序取TOP商品列表，列表信息包括：商品基础信息、销售数据、近30天视频销量趋势。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| day_type | 是 | 榜单周期类型：day（日榜）、week（周榜）、month（月榜），必填 |
| day | 是 | 榜单周期，示例：2025-02-23（日榜周期），20250217-20250223（周榜周期）、202501（月榜周期），必填 |
| category_id | 否 | 商品分类ID/商品分类名称(示例：食品饮料、护肤品），非必填 |
| is_new_product | 否 | 填1筛选周期内新上架商品，非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| day | 日榜 |
| week | 周榜 |
| month | 月榜 |

`is_new_product`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新上架商品 |

示例:

```json
{
  "day": "2025-02-23",
  "day_type": "day"
}
```

### product_key_metrics_live_video_author_sales_data_period_total

- 摘要：获取指定商品在周期内的关键数据指标，返回周期内各指标的合计值，包括：商品数据、销售数据、关联直播数据、关联视频数据、关联达人数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| promotion_id | 是 | 指定单个商品ID/商品标题，必填 |
| start_date | 是 | 开始时间，必填 |
| end_date | 是 | 结束时间，必填 |

示例:

```json
{
  "promotion_id": "DBEKKfrXM--cyWvIzvIp43VcschhyE3x",
  "start_date": "2026-07-22",
  "end_date": "2026-08-20"
}
```
