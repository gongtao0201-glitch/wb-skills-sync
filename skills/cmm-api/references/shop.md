# 小店 API 参考

仅当用户的 CMM 请求主要属于该实体领域时使用此文件。

## 分类默认查询字段

适用时使用该分类的默认查询字段。

## API 索引

| API | 摘要 |
| --- | --- |
| shop_audience_profile | 获取指定小店的直播视频观众画像，观众画像包括： 性别、年龄、地区、城市等级 、视频内容偏好。 |
| shop_related_commerce_author_list | 获取指定小店在周期内关联的带货达人列表，列表信息包含：达人基础信息、该达人归属小店的销售数据（示例：销量、销售额、关联直播数、关联视频数等） |
| shop_library_custom_search_shop | 通过小店基础信息和小店关键数据指标多条件组合，筛选出满足条件的小店列表，支持按指定指标排序。列表信息包括：小店名称、小店logo、小店数据指标。 |
| shop_basic_info | 获取指定小店的基础信息。 |
| shop_order_profile | 获取指定小店的成交画像，成交画像类型包括： 性别、年龄、地区。 |
| shop_related_product_list | 获取指定小店在周期内的动销商品列表，列表信息包括：商品基础信息及商品数据指标 |
| shop_related_commerce_live_list | 获取指定小店在周期内关联的带货直播列表，列表信息包括：直播基础信息、该直播间归属小店的销售数据。 |
| shop_related_commerce_video_list | 获取指定小店在周期内关联的带货视频列表，列表信息包括：视频基础信息、视频的销售数据。 |
| shop_key_metrics_live_video_author_sales_data_period_total | 获取指定小店在周期内的关键数据指标，返回周期内各指标的合计值，包括小店数据、销售数据、关联达人数据、关联直播数据、关联视频数据。 |
| shop_key_metrics_live_video_author_sales_data_daily_detail | 获取指定小店在周期内的关键数据指标明细，按日返回各数据指标值，包括小店数据、销售数据、关联达人数据、关联直播数据、关联视频数据。 |
| shop_related_category_list | 获取指定小店在周期内动销的品类列表，列表信息包括：品类数据指标。 |
| shop_related_product_list_2 | 获取指定小店在周期内的动销商品卡列表，列表信息包括：有商品卡动销的商品基础信息及商品数据指标。 |
| shop_top_selling_shop_rank_period | 获取历史周期的小店热销榜单，榜单按周期内小店销售额降序取TOP小店列表，列表信息包括：小店基础信息、小店销售数据。 |
| shop_top_selling_brand_shop_rank_period | 获取历史周期的品牌官方小店热销榜单，榜单按周期内品牌官方小店销售额降序取TOP小店列表，列表信息包括：小店基础信息、小店销售数据。 |
## API 详情

### shop_audience_profile

- 摘要：获取指定小店的直播视频观众画像，观众画像包括： 性别、年龄、地区、城市等级 、视频内容偏好。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |

示例:

```json
{
  "shop_id": "ujRztTIP"
}
```

### shop_related_commerce_author_list

- 摘要：获取指定小店在周期内关联的带货达人列表，列表信息包含：达人基础信息、该达人归属小店的销售数据（示例：销量、销售额、关联直播数、关联视频数等）

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |
| is_new_corp | 否 | 填1筛选出新合作达人，非必填 |
| channels | 否 | 达人类型：brand_self_author（品牌自营号）、shop_self_author（商家自营号）、common_author（达人号），非必填 |
| follower_count | 否 | 粉丝数区间，格式最小值-最大值（如0-1000），非必填 |
| sale_way | 否 | 带货方式：1（直播带货）、2（视频带货），非必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、follower_count（粉丝数）、room_count（关联带货直播数）、aweme_count（关联带货视频数）、product_count(动销商品数)，非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`is_new_corp`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新合作达人 |

`channels`:

| 取值 | 含义 |
| --- | --- |
| brand_self_author | 品牌自营号 |
| shop_self_author | 商家自营号 |
| common_author | 达人号 |

`sale_way`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选有直播带货的达人 |
| 2 | 筛选有视频带货的达人 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| follower_count | 粉丝数 |
| reputation_score | 达人带货口碑 |
| aweme_count | 关联视频数 |
| live_count | 关联直播数 |
| product_count | 动销商品数 |
| volume | 销量 |
| amount | 销售额 |

示例:

```json
{
  "shop_id": "ujRztTIP",
  "start_time": "2025-01-25",
  "end_time": "2025-02-23"
}
```

### shop_library_custom_search_shop

- 摘要：通过小店基础信息和小店关键数据指标多条件组合，筛选出满足条件的小店列表，支持按指定指标排序。列表信息包括：小店名称、小店logo、小店数据指标。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| category_id | 否 | 商品名称/商品分类，可填写商品品类名称或ID(示例：食品饮料、护肤品、牙膏），非必填 |
| day_type | 否 | 可选查询周期：day（昨天）、week（近7天）、month（近30天），非必填 |
| duration_avg_price | 否 | 客单价区间，格式最小值-最大值（如0-1000），非必填 |
| duration_avg_amount | 否 | 周期内销售额区间，格式最小值-最大值（如0-1000），非必填 |
| most_volume | 否 | 销售方式：1（视频带货为主）、2（直播带货为主）、3（商品卡带货为主），非必填 |
| channel | 否 | 带货渠道：1（达人号为主）、2（品牌自营号为主）、3（商家自营号为主），非必填 |
| deliver_area | 否 | 主要发货地，如：福建省，仅支持单个省份，非必填 |
| is_new_product | 否 | 填1筛选周期内新上架商品，非必填 |
| fans_gender | 否 | 受众画像性别，-1（不限）、0（男性居多）、1（女性居多），非必填 |
| fans_age | 否 | 受众画像年龄区间，1（18-23岁）、2（24-30岁）、3（31-40岁）、4（41-50岁）、5（50岁以上），单选，非必填 |
| bring_channel_brand | 否 | 填1筛选品牌自营销售为主的小店，非必填 |
| bring_channel_shop | 否 | 填1筛选商家自营销售为主的小店，非必填 |
| bring_channel_author | 否 | 填1筛选达人号销售为主的小店，非必填 |
| most_live_volume | 否 | 填51筛选直播带货为主的小店，非必填 |
| most_aweme_volume | 否 | 填51筛选视频带货为主的小店，非必填 |
| sort | 否 | 排序字段：total_product_num（动销商品数）、dvolume（销量）、amount（销售额）、author_count（关联达人数），非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`fans_gender`:

| 取值 | 含义 |
| --- | --- |
| -1 | 不限 |
| 0 | 男性居多 |
| 1 | 女性居多 |

`fans_age`:

| 取值 | 含义 |
| --- | --- |
| 2 | 18-23岁 |
| 3 | 24-30岁 |
| 4 | 31-40岁 |
| 5 | 41-50岁 |
| 6 | 50岁以上 |

`bring_channel_brand`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选品牌自营号带货为主的小店 |

`bring_channel_shop`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选商家自营号带货为主的小店 |

`bring_channel_author`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选达人号带货为主的小店 |

`most_live_volume`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 51 | 筛选直播带货为主的小店 |

`most_aweme_volume`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 51 | 筛选视频带货为主的小店 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| amount | 销售额 |
| volume | 销量 |
| total_product_num | 动销商品数 |
| expr_score | 商品体验分 |
| author_count | 关联带货达人数 |
| live_count | 关联带货直播数 |
| aweme_count | 关联带货视频数 |

示例:

```json
{}
```

### shop_basic_info

- 摘要：获取指定小店的基础信息。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |

示例:

```json
{
  "shop_id": "YJTDSPQb"
}
```

### shop_order_profile

- 摘要：获取指定小店的成交画像，成交画像类型包括： 性别、年龄、地区。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |

示例:

```json
{
  "shop_id": "ujRztTIP"
}
```

### shop_related_product_list

- 摘要：获取指定小店在周期内的动销商品列表，列表信息包括：商品基础信息及商品数据指标

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |
| keyword | 否 | 商品标题关键词（示例：面包、洗面奶），非必填 |
| is_new_corp | 否 | 填1筛选出新上架商品，非必填 |
| bring_way | 否 | 带货方式，1（直播带货为主）、2（视频带货为主），非必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、price（商品价格）、live_count（关联带货直播数）、aweme_count（关联带货视频数）、author_count(关联带货达人数)，非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`is_new_corp`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选新上架商品 |

`bring_way`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选直播带货为主 |
| 2 | 筛选视频带货为主的商品 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| amount | 销售额 |
| price | 商品价格 |
| volume | 销量 |
| author_count | 关联带货达人数 |
| live_count | 关联带货直播数 |
| aweme_count | 关联带货视频数 |

示例:

```json
{
  "shop_id": "ZbjtlPn",
  "start_time": "2025-01-25",
  "end_time": "2025-02-23"
}
```

### shop_related_commerce_live_list

- 摘要：获取指定小店在周期内关联的带货直播列表，列表信息包括：直播基础信息、该直播间归属小店的销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |
| channels | 否 | 直播达人类型，brand_self_author（品牌自营号）、shop_self_author（商家自营号）、common_author（达人号），非必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、begin_time（开播时间）、watch_count（观看人次）、shop_product_count（小店商品数），非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`channels`:

| 取值 | 含义 |
| --- | --- |
| brand_self_author | 品牌自营号 |
| shop_self_author | 商家自营号 |
| common_author | 达人号 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| amount | 销售额 |
| begin_time | 开播时间 |
| watch_count | 观看人次 |
| shop_product_count | 小店商品数 |
| volume | 销量 |

示例:

```json
{
  "shop_id": "TxXWfZdq",
  "start_time": "2025-01-25",
  "end_time": "2025-02-23"
}
```

### shop_related_commerce_video_list

- 摘要：获取指定小店在周期内关联的带货视频列表，列表信息包括：视频基础信息、视频的销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |
| is_new_corp | 否 | 填1筛选出周期内新发布视频，非必填 |
| sort | 否 | 排序字段：volume（销量）、amount（销售额）、digg_count（点赞数）、comment_count（评论数）、share_count（转发数），非必填 |
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
| amount | 销量 |
| share_count | 转发数 |
| comment_count | 评论数 |
| digg_count | 点赞数 |
| volume | 销售额 |

示例:

```json
{
  "shop_id": "YJTDSPQb",
  "start_time": "2025-02-18",
  "end_time": "2025-03-19"
}
```

### shop_key_metrics_live_video_author_sales_data_period_total

- 摘要：获取指定小店在周期内的关键数据指标，返回周期内各指标的合计值，包括小店数据、销售数据、关联达人数据、关联直播数据、关联视频数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_date | 是 | 开始时间，必填 |
| end_date | 是 | 结束时间，必填 |

示例:

```json
{
  "shop_id": "KMFNULt",
  "start_date": "2025-02-23",
  "end_date": "2025-02-23"
}
```

### shop_key_metrics_live_video_author_sales_data_daily_detail

- 摘要：获取指定小店在周期内的关键数据指标明细，按日返回各数据指标值，包括小店数据、销售数据、关联达人数据、关联直播数据、关联视频数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |
| page | 否 | 页码，默认为第1页（每页返回31条），非必填 |

示例:

```json
{
  "shop_id": "KMFNULt",
  "start_time": "2025-02-14",
  "end_time": "2025-02-14"
}
```

### shop_related_category_list

- 摘要：获取指定小店在周期内动销的品类列表，列表信息包括：品类数据指标。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |

示例:

```json
{
  "shop_id": "YJTDSPQb",
  "start_time": "2025-01-02",
  "end_time": "2025-02-02"
}
```

### shop_related_product_list_2

- 摘要：获取指定小店在周期内的动销商品卡列表，列表信息包括：有商品卡动销的商品基础信息及商品数据指标。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| shop_id | 是 | 指定单个小店ID/小店名称，必填 |
| start_time | 是 | 开始时间，必填 |
| end_time | 是 | 结束时间，必填 |
| keyword | 否 | 商品标题关键词（示例：面包、洗面奶），非必填 |
| is_new_corp | 否 | 填1筛选出新上架商品，非必填 |
| sort | 否 | 排序字段：other_volume（商品卡销量）、other_amount（商品卡销售额）、price（商品价格），非必填 |
| page | 否 | 页码，默认为第1页（每页返回10条），非必填 |

- 枚举值:

`is_new_corp`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选周期内新上架商品 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| other_amount | 销售额 |
| price | 成交价 |
| other_volume | 销量 |

示例:

```json
{
  "shop_id": "TxXWfZdq",
  "start_time": "2025-01-25",
  "end_time": "2025-02-23"
}
```

### shop_top_selling_shop_rank_period

- 摘要：获取历史周期的小店热销榜单，榜单按周期内小店销售额降序取TOP小店列表，列表信息包括：小店基础信息、小店销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| day_type | 是 | 榜单周期类型：day（日榜）、week（周榜/大促周期）、month（月榜）、season （季度榜）、half_year（半年榜）、year（年榜），必填 |
| day | 是 | 榜单周期，示例：2025-02-23（日榜周期），20250217-20250223（周榜周期）、202501（月榜周期），202601-202612（季度/半年/年周期），20260515-20260618（大促周期，确保数据查询范围与【蝉妈妈大促数据周期】一致），必填 |
| big_promotion | 否 | 填1表示week为大促周期，只支持系统提供【蝉妈妈大促数据周期】，其余大促请勿使用大促周期查询。非必填 |
| category_id | 否 | 商品分类ID/商品分类名称(示例：食品饮料、护肤品），非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| day | 日榜 |
| week | 周榜 |
| month | 月榜 |

示例:

```json
{
  "day": "2025-02-23",
  "day_type": "day"
}
```

### shop_top_selling_brand_shop_rank_period

- 摘要：获取历史周期的品牌官方小店热销榜单，榜单按周期内品牌官方小店销售额降序取TOP小店列表，列表信息包括：小店基础信息、小店销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| day_type | 是 | 榜单周期类型：day（日榜）、week（周榜）、month（月榜），必填 |
| day | 是 | 榜单周期，示例：2025-02-23（日榜周期），20250217-20250223（周榜周期）、202501（月榜周期），必填 |
| category_id | 否 | 商品分类ID/商品分类名称(示例：食品饮料、护肤品），非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`day_type`:

| 取值 | 含义 |
| --- | --- |
| day | 日榜 |
| week | 周榜 |
| month | 月榜 |

示例:

```json
{
  "day": "2025-02-23",
  "day_type": "day"
}
```
