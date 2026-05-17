# 数据模型

## 建模原则

第一阶段模型围绕数字孪生场景展开。所有数据都必须能回答：属于哪个场景、哪个地块、哪个指标、哪个时间、哪个批次、哪个来源、质量状态是什么。

## 核心实体

| 实体 | 说明 |
|---|---|
| `TwinScenario` | 数字孪生场景，承载名称、说明、数据模式、地块数、指标数和时间范围 |
| `Plot` | 地块，包含编号、名称、区域、边界和状态 |
| `Metric` | 指标字典，定义编码、名称、类别、单位、正常范围和色阶 |
| `MetricObservation` | 指标观测长表，记录某地块某指标某日期的值 |
| `ObservationBatch` | 观测批次，记录模拟数据生成批次或后续正式数据批次 |
| `DataSource` | 数据来源，区分模拟数据、程序生成边界、PostGIS、遥感或传感器 |
| `DataQualityIssue` | 数据质量或状态问题，记录缺失、异常和错误预警 |

## 当前默认场景

| 字段 | 值 |
|---|---|
| 场景 ID | `demo-ricefield-2025` |
| 地块 | 8 个程序生成矩形地块 |
| 区域 | 试验一区、试验二区 |
| 指标 | 11 个 |
| 时间范围 | 2025-06-01 至 2025-07-15 |
| 预警 | 2 个缺失点、4 个异常点 |

## 关键字段

`MetricObservation` 必须包含：

- `id`
- `plot_id`
- `plot_code`
- `metric_code`
- `value`
- `unit`
- `observed_at`
- `batch_id`
- `data_source_id`
- `quality_flag`

第一阶段前端不展示 `source_file`、`raw_sheet`、`raw_cell` 等 Excel 定位字段。

## PostGIS 说明

现有数据库表仍可短期使用历史表名，但代码语义已迁移：

- `import_batches` 作为 `ObservationBatch` 兼容表。
- `import_issues` 作为 `DataQualityIssue` 兼容表。
- `metric_observations.import_batch_id` 在 API 层映射为 `batch_id`。

后续正式迁移时再新增 `twin_scenarios`、`data_sources`、`observation_batches`、`data_quality_issues` 等更准确表名。
