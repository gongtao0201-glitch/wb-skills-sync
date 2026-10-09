# 视频工具参考

用于处理单条视频内容。查询视频榜单、指标、详情或评论时，应改读 `references/video.md`。

## 使用规则

- 口播文案工具必须提供 `video_url`，支持蝉妈妈、抖音平台视频链接；`video_id` 是可选的蝉妈妈视频 ID，两者同时提供时优先使用 `video_url`。
- 口播文案工具不支持千川素材的 `material_id` 或 `cy.chanmama` 平台视频链接。
- 视频分镜工具的 `video_url` 与 `video_id` 至少提供一个；两者同时提供时优先使用 `video_url`。
- 视频分镜的 `video_url` 支持蝉妈妈、抖音平台视频链接，`video_id` 是蝉妈妈视频 ID。
- 视频画面理解的 `video_urls` 是非空视频链接数组，支持平台视频链接或直接的视频文件播放地址。平台链接会自动获取播放地址后理解，直接播放地址会直接理解。
- 视频画面理解默认不要传 `custom_prompt`，让工具使用系统提示词返回视频形式、剪辑、内容描述和每个分镜的画面内容；仅在用户明确提出针对性分析要求时传入 `custom_prompt`。
- 视频画面理解不支持 `cy.chanmama` 平台的视频链接。
- 视频画面理解是异步任务；`scripts/call_cmm_api.py` 会通过同一个 `/v1/cmm/api/execute` 自动创建并轮询到终态。

## API 索引

| API | 摘要 |
| --- | --- |
| `extract_video_copywriting` | 根据视频链接提取口播/旁白文案，返回纯文本。 |
| `video_storyboard` | 拆解视频分镜，返回时间段、片段地址和语音文字。 |
| `video_understanding` | 理解一个或多个视频的画面、动作和内容，可使用自定义提示词。 |

## API 详情

### extract_video_copywriting

- 摘要：根据视频链接提取视频中的口播/旁白文案，返回纯文本结果。
- 适用场景：用户要求提取台词、口播、字幕文案或视频文字内容。
- 平台限制：不支持千川素材的 `material_id` 或 `cy.chanmama` 平台视频链接。

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| `video_url` | 是 | 视频链接，支持蝉妈妈、抖音平台的视频链接。 |
| `video_id` | 否 | 可选的蝉妈妈视频 ID；与 `video_url` 同时提供时优先使用 `video_url`，不能替代必填的 `video_url`。 |

示例：

```json
{
  "api": "extract_video_copywriting",
  "query": {
    "video_url": "https://example.com/video.mp4"
  }
}
```

成功响应的 `data` 为提取出的口播/旁白纯文本字符串。

### video_storyboard

- 摘要：对视频进行分镜画面拆解并提取，返回每个分镜的开始时间 `st`、结束时间 `ed`、片段视频地址 `clip_video_url` 和语音文字 `voice`。
- 适用场景：用户要求分析镜头结构、分镜时间、片段画面或每段语音文字。

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| `video_url` | 与 `video_id` 至少提供一个 | 视频链接，支持蝉妈妈、抖音平台的视频链接；两者都提供时优先使用此字段。 |
| `video_id` | 与 `video_url` 至少提供一个 | 蝉妈妈视频 ID；两者都提供时优先使用 `video_url`。 |

示例：

```json
{
  "api": "video_storyboard",
  "query": {
    "video_url": "https://example.com/video.mp4"
  }
}
```

成功响应的 `data` 包含：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `video_title` | string | 视频标题。 |
| `video_url` | string | 视频地址。 |
| `duration` | number | 视频时长。 |
| `result` | array | 分镜列表。 |

`result` 中每个分镜包含开始时间 `st`、结束时间 `ed`、片段视频地址 `clip_video_url` 和语音文字 `voice`。

### video_understanding

- 摘要：理解一个或多个视频的画面内容。默认使用系统提示词，返回视频形式、剪辑、内容描述、每个分镜的画面内容，并结合首帧信息和台词/旁白生成 Markdown 分析；也可按用户明确给出的自定义提示词进行针对性理解。
- 适用场景：用户要求描述视频画面、分析人物动作、场景、镜头变化、视觉风格或按自定义维度理解视频。
- 链接处理：平台视频链接会自动获取视频播放地址后理解，直接的视频文件播放地址会直接理解；不支持 `cy.chanmama` 平台的视频链接。

查询字段：

| 查询字段 | 是否必填 | 说明 |
| --- | --- | --- |
| `video_urls` | 是 | 非空视频链接数组；单个视频也必须使用数组。支持平台视频链接或直接的视频文件播放地址。 |
| `custom_prompt` | 否 | 默认不传。仅当用户明确提出针对性理解要求时传入；不传时使用系统默认提示词。 |

示例：

```json
{
  "api": "video_understanding",
  "query": {
    "video_urls": ["https://example.com/video.mp4"]
  }
}
```

调用 `scripts/call_cmm_api.py` 时无需手工查询任务。脚本内部使用 `video_understanding_task_info` 轮询，并在 `succeeded` 或 `failed` 后输出最终响应。ChatBI 统一响应中的任务位于 `data.data`，成功任务的 `data.data.result` 包含 Markdown 内容。
