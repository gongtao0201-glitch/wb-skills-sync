# 直播 API 参考

仅当用户的 CMM 请求主要属于该实体领域时使用此文件。

## 分类默认查询字段

适用时使用该分类的默认查询字段。

## API 索引

| API | 摘要 |
| --- | --- |
| live_live | 获取指定直播间从开播到下播，各个时间点的场观明细、直播间观众画像及弹幕热词 |
| live_library_custom_search_live | 通过主播名称关键字、直播基础信息和直播关键数据指标多条件组合，筛选出满足条件的热门直播列表，支持按指定指标排序。列表信息包括：直播标题、直播头图、直播数据指标。 |
| live_basic_info_product_list_audience_profile | 获取指定直播场次的基础信息、关键数据指标及带货商品列表。 |
| live_top_selling_commerce_live_rank_rank | 获取今日热销带货直播间榜单，列表包括：直播基础信息、直播销售数据。 |
| live_room_barrage_detail | 获取制定直播场次的弹幕原文明细。 |
| live_commerce_hour_rank | 获取抖音官方指定日期指定小时（含今日实时）的榜单数据，支持近90天内任意日期的历史榜单查询，列表包括：直播基础信息、直播销售数据。 |
## API 详情

### live_live

- 摘要：获取指定直播间从开播到下播，各个时间点的场观明细、直播间观众画像及弹幕热词

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| room_id | 是 | 指定单个直播间ID/直播间名称，必填 |

示例:

```json
{
  "room_id": "7kONmB2vmD7TU6odLaNJWYWSNShf7L_u"
}
```

### live_library_custom_search_live

- 摘要：通过主播名称关键字、直播基础信息和直播关键数据指标多条件组合，筛选出满足条件的热门直播列表，支持按指定指标排序。列表信息包括：直播标题、直播头图、直播数据指标。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | 否 | 直播达人名称（示例：贾乃亮），非必填 |
| multi_category_id | 否 | 带货商品分类ID/带货商品品类名称/商品名称，多选时按逗号分隔，非必填 |
| star_category | 否 | 达人视频分类名称或ID(示例：亲子、穿搭），非必填 |
| live_begin_time | 是 | 开始日期（示例：2025-05-02），必填 |
| live_end_time | 是 | 结束日期（示例：2025-05-02），必填 |
| province | 否 | 直播省份(示例：福建省），非必填 |
| follower_count | 否 | 粉丝数区间，格式最小值-最大值（如0-1000），非必填 |
| volume | 否 | 直播销量区间，格式最小值-最大值（如0-1000），非必填 |
| is_brand_exclusive | 否 | 填1筛选品牌自播直播间，非必填 |
| is_take_product | 否 | 填1带货直播间，非必填 |
| sort | 否 | 排序字段：amount（销售额）、volume（销量）、begin_time（开播时间）、total_user（场观）、user_peak（人气峰值）、duration（直播时长）、product_size（商品数），非必填 |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`is_brand_exclusive`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 品牌自播直播间 |

`is_take_product`:

| 取值 | 含义 |
| --- | --- |
| 0 | 不限 |
| 1 | 筛选带货直播间 |

`sort`:

| 取值 | 含义 |
| --- | --- |
| total_user | 观看人次 |
| user_peak | 人气峰值 |
| begin_time | 开播时间 |
| duration | 直播时长 |
| product_size | 商品数 |
| amount | 销售额 |
| volume | 销量 |

示例:

```json
{
  "live_begin_time": "",
  "live_end_time": ""
}
```

### live_basic_info_product_list_audience_profile

- 摘要：获取指定直播场次的基础信息、关键数据指标及带货商品列表。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| room_id | 是 | 指定单个直播间ID/直播间名称，必填 |

示例:

```json
{
  "room_id": "lRFH_lYSnN3u2fFXfrBeo1Xa9-h-dq9L"
}
```

### live_top_selling_commerce_live_rank_rank

- 摘要：获取今日热销带货直播间榜单，列表包括：直播基础信息、直播销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| category_id | 否 | 带货商品分类ID/带货商品分类名称(示例：食品饮料、护肤品），非必填 |
| star_category | 否 | 达人视频分类名称或ID(示例：亲子、穿搭），非必填 |
| is_brand_self | 否 | 填1筛选品牌自播直播间，非必填 |
| orderby | 否 | 排序字段：amount（销售额）、volume（销量）、score（带货热度）、user_peak（本场直播人气峰值）、follower_count（达人粉丝数），默认：amount |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`is_brand_self`:

| 取值 | 含义 |
| --- | --- |
| 0 | 否 |
| 1 | 是 |

示例:

```json
{}
```

### live_room_barrage_detail

- 摘要：获取制定直播场次的弹幕原文明细。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| room_id | 是 | 指定单个直播间ID/直播间名称，必填 |
| limit | 否 | 条数限制，默认50 |

示例:

```json
{
  "room_id": "cWQhpMscX7KNTMC5GeGGGpw6GxE3ojS9"
}
```

### live_commerce_hour_rank

- 摘要：获取抖音官方指定日期指定小时（含今日实时）的榜单数据，支持近90天内任意日期的历史榜单查询，列表包括：直播基础信息、直播销售数据。

- 参数:

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| date | 否 | 查询日期，支持近90天内任意历史日期（含今日），示例：2026-08-11 |
| hour | 否 | 查询小时，使用自然小时, 取值从0到23 |
| star_category | 否 | 达人视频分类名称或ID(示例：亲子、穿搭），非必填 |
| category_name | 是 | 榜单类别，可选值：总榜、珠光宝气、摄影摄像、床上用品、粮油调味、亲子装、零食特产、彩妆香水、国家补贴、抖音旗舰、个人护理、内衣裤袜、生鲜、手机、女装、女鞋、箱包，必填 |
| product_category | 是 | 与category_name传一样的值，必填 |
| orderby | 否 | 排序字段：amount（销售额）、volume（销量）、score（抖音官方带货热度）、follower_count（达人粉丝数），推荐排序：score |
| page | 否 | 页码，默认为第1页（每页返回50条），非必填 |

- 枚举值:

`orderby`:

| 取值 | 含义 |
| --- | --- |
| score | 抖音官方带货热度 |
| amount | 直播销售额 |
| volume | 直播销量 |
| follower_count | 粉丝数 |

示例:

```json
{
  "product_category": "总榜",
  "category_name": "总榜"
}
```
