# 数据模型

## 建模原则

数据模型以“地块、指标、观测值、导入批次、质量问题”为核心。Excel 原始字段进入系统后必须转换为统一长表结构，前端和 API 不直接依赖原始 Excel 表格形态。

第一版数据模型暂不连接数据库，先用 Pydantic schema 约束内存数据、导入输出和后续 API 响应。对应代码位于 `backend/app/schemas/data_model.py`。

## 核心实体

### Metric 指标

| 字段 | 类型 | 含义 |
|---|---|---|
| `metric_code` | str | 指标编码 |
| `metric_name` | str | 中文名称 |
| `category` | str | 指标类别 |
| `unit` | str | 标准单位 |
| `value_type` | `float` / `int` | 数值类型 |
| `precision` | int | 小数位数 |
| `normal_range` | object | 正常范围，包含 `min` 和 `max` |
| `color_scale` | str | 地图着色方案 |
| `description` | str | 指标说明 |
| `source_type` | `excel` / `geojson` / `manual` | 数据来源类型 |

### Plot 地块

| 字段 | 类型 | 含义 |
|---|---|---|
| `plot_id` | str | 地块唯一 ID |
| `plot_code` | str | 地块编号 |
| `plot_name` | str / null | 地块名称或别名 |
| `region` | str / null | 所属区域，如东区、西区 |
| `geometry` | object / null | 地块空间边界，来源于 GeoJSON |
| `status` | str | 地块状态，第一版默认 `normal` |

### MetricObservation 指标观测值

统一长表结构用于承接 Excel 解析后的标准化观测记录。每一行只描述“某个地块在某个时间的某一个指标值”。

| 字段 | 类型 | 含义 |
|---|---|---|
| `id` | str | 记录 ID |
| `plot_id` | str | 地块 ID |
| `plot_code` | str | 地块编号 |
| `metric_code` | str | 指标编码 |
| `value` | float / int / null | 指标值，缺失或错误时可为空 |
| `unit` | str | 单位，来自指标字典 |
| `observed_at` | date | 观测日期 |
| `import_batch_id` | str | 导入批次 ID |
| `source_file` | str | 来源文件 |
| `raw_sheet` | str / null | 来源工作表 |
| `raw_cell` | str / null | 来源单元格，如 `C2` |
| `quality_flag` | `normal` / `missing` / `outlier` / `error` | 数据质量标记 |

第一版 Excel 解析服务会为每个可定位到地块和日期的指标单元格生成一条记录。标准宽表直接按指标编码列展开；研究数据导出格式按 `type` 映射指标编码，并把每个 `地块编号:"数值"` 单元格拆成一条记录。缺失值、异常值和无法解析的指标值不会被静默丢弃，而是通过 `quality_flag` 标记，并进入导入质量报告。

### ImportBatch 导入批次

| 字段 | 类型 | 含义 |
|---|---|---|
| `import_batch_id` | str | 导入批次 ID |
| `source_file` | str | 来源文件名 |
| `imported_at` | datetime | 导入时间 |
| `status` | `pending` / `processing` / `success` / `failed` / `partial_success` / `partial` | 导入状态 |
| `record_count` | int | 成功记录数 |
| `warning_count` | int | 警告数量 |
| `error_count` | int | 错误数量 |

### ImportIssue 导入质量问题

| 字段 | 类型 | 含义 |
|---|---|---|
| `issue_id` | str | 问题 ID |
| `import_batch_id` | str | 导入批次 ID |
| `issue_type` | str | 问题类型 |
| `severity` | `info` / `warning` / `error` | 严重级别 |
| `message` | str | 中文说明 |
| `source_file` | str | 来源文件 |
| `raw_sheet` | str / null | 来源工作表 |
| `raw_cell` | str / null | 来源单元格 |
| `plot_code` | str / null | 关联地块编号 |
| `metric_code` | str / null | 关联指标编码 |

### ImportQualityReport 导入质量报告

每次 Excel 导入都必须生成质量报告，供导入中心展示和后续 API 返回。

| 字段 | 类型 | 含义 |
|---|---|---|
| `import_batch_id` | str | 导入批次 ID |
| `source_file` | str | 文件名称 |
| `successful_record_count` | int | 成功记录数，即 `quality_flag=normal` 的记录数 |
| `missing_value_count` | int | 缺失值数量 |
| `outlier_count` | int | 异常值数量 |
| `unmatched_plots` | list[str] | 未匹配地块编号列表 |
| `error_cells` | list[str] | 错误单元格列表 |
| `skipped_record_count` | int | 跳过的指标单元格数量 |
| `parse_duration_ms` | int | 解析耗时，单位毫秒 |
| `status` | `success` / `partial` / `failed` | 导入状态 |
| `parse_errors` | list[str] | 工作表级或文件级解析错误说明 |

## 追溯规则

每条 `MetricObservation` 必须保留 `plot_code`、`metric_code`、`observed_at`、`import_batch_id`、`source_file`、`raw_sheet`、`raw_cell` 和 `quality_flag`。导入服务不得隐藏缺失值、异常值、无法解析的单元格或未匹配地块，应转化为观测记录、质量报告字段或后续可落库的 `ImportIssue`。

## 后续补充

正式接入 PostgreSQL + PostGIS 前，需要将以上 Pydantic schema 细化为数据库表结构、索引、空间字段和 Alembic 迁移策略。MVP 阶段可以先输出标准化 JSON / CSV，用相同字段对齐后续数据库设计。
