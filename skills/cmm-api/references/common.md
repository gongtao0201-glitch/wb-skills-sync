# 通用搜索 API 参考


**核心原则：名称优先搜索转ID**

当用户提供的是**名称而非ID**时，且**上下文中无法获得对应ID**时，**必须先调用此文件中的搜索API转换为ID**，然后再调用业务API。

## 使用场景

| 用户输入示例 | 判断 | 处理方式 |
|-------------|------|---------|
| "查询达人：李佳琦" | 名称 | ✅ 先调用 `author_search` 转为 author_id |
| "查询达人ID：123456" | ID | ❌ 直接使用，无需搜索 |
| "护肤品类目的商品" | 名称 | ✅ 先调用 `product_category_search` 转为 category_id |
| "亲子类达人" | 达人视频分类名称 | ✅ 先调用 `author_category_search` 转为达人分类值 |
| "category_id=1001的商品" | ID | ❌ 直接使用，无需搜索 |
| "花西子品牌的销售数据" | 名称 | ✅ 先调用 `brand_search` 转为 brand_code |
| 之前对话已获得李佳琦的author_id | 上下文已知 | ❌ 直接使用上下文中的ID，无需重复搜索 |

**重要提示**：
- 用户输入的实体名称（达人昵称、商品标题、品牌名、店铺名等）需要先搜索转ID
- 用户输入达人内容/视频分类名称（如亲子、美妆等）筛选达人时，先搜索达人视频分类，避免直接把自然语言填入分类字段
- 只有当用户明确提供纯数字ID或明确说明是ID时，才可直接使用
- **如果从上下文（之前的对话、API响应等）中已经获得了对应的ID，直接使用，无需重复搜索**
- 如果搜索返回多个结果，向用户展示列表并让用户选择


## API 索引

| API | 摘要 |
| --- | --- |
| product_category_search | Search product category names and return matching category IDs. |
| author_category_search | Search author video category names and return matching author category names/paths. |
| product_search | Search products by name or Douyin product link and return matching product IDs. |
| author_search | Search authors by name and return matching author IDs. |
| shop_search | Search shops by name and return matching shop IDs. |
| brand_search | Search brands by name and return matching brand IDs. |
| video_search | Search videos by title or Douyin video link and return matching video IDs. |

## API 详情

### product_category_search

- 摘要：Search product category names and return matching category IDs.
- 使用场景：Use when the user needs to convert a product category/class name into category_id.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Product category name keyword, e.g. 护肤品 or 女鞋. |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| category_id | integer/string | Product category ID. |
| category_name | string/array | Matched category name. |
| category_full_name | string | Full category path when available. |

### author_category_search

- 摘要：Search author video category names and return matching author category names/paths.
- 使用场景：Use when the user needs to convert an author video category/class name into the category value used by author APIs, such as star_category/full_author_category.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Author video category name keyword, e.g. 亲子 or 美妆. |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| category_name | string | Matched author video category name. |
| category_full_name | string | Full author video category path when available. |

### product_search

- 摘要：Search products by name or Douyin product link and return matching product IDs.
- 使用场景：When user provides a product name or Douyin product link, call this API to convert to promotion_id.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Product name keyword OR Douyin product link (supports full URL or short link). |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| promotion_id | string | Product ID. |
| title | string | Product title. |

### author_search

- 摘要：Search authors by name and return matching author IDs.
- 使用场景：Use when the user needs to convert an author name into author_id.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Author nickname keyword. |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| author_id | string | Author ID. |
| nickname | string | Author nickname. |

### shop_search

- 摘要：Search shops by name and return matching shop IDs.
- 使用场景：Use when the user needs to convert a shop name into shop_id.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Shop name keyword. |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| shop_id | string | Shop ID. |
| name | string | Shop name. |

### brand_search

- 摘要：Search brands by name and return matching brand IDs.
- 使用场景：Use when the user needs to convert a brand name into brand_code.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Brand name keyword. |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| brand_code | string | Brand ID/code. |
| brand_name | string | Brand name. |

### video_search

- 摘要：Search videos by title or Douyin video link and return matching video IDs.
- 使用场景：When user provides a video title or Douyin video link, call this API to convert to aweme_id.

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| keyword | yes | Video title keyword OR Douyin video link (supports full URL or short link). |

响应字段提示：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| aweme_id | string | Video ID. |
| title | string | Video title. |
