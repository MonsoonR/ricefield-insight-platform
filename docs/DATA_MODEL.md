# 数据模型

## 建模原则

数据模型以“地块、指标、观测值、导入批次、质量问题”为核心。Excel 原始字段进入系统后应转换为统一长表结构，前端和 API 不直接依赖原始 Excel 表格形态。

## 核心实体

### 地块 Plot

| 字段 | 含义 |
|---|---|
| plot_id | 地块唯一 ID |
| plot_code | 地块编号 |
| plot_name | 地块名称或别名 |
| region | 所属区域，如东区、西区 |
| geometry | 地块空间边界，来源于 GeoJSON |
| status | 地块状态，如正常、无数据、异常 |

### 指标 Metric

| 字段 | 含义 |
|---|---|
| metric_code | 指标编码 |
| metric_name | 中文名称 |
| category | 指标类别 |
| unit | 标准单位 |
| value_type | 数值类型 |
| precision | 小数位数 |
| normal_range | 正常范围 |
| color_scale | 地图着色方案 |
| description | 指标说明 |
| source_type | 数据来源类型 |

### 观测值 Observation

| 字段 | 含义 |
|---|---|
| id | 记录 ID |
| plot_id | 地块 ID |
| plot_code | 原始或标准化地块编号 |
| metric_code | 指标编码 |
| value | 指标值 |
| unit | 单位 |
| observed_at | 观测日期 |
| import_batch_id | 导入批次 ID |
| source_file | 来源文件 |
| raw_sheet | 来源工作表 |
| raw_cell | 来源单元格 |
| quality_flag | 数据质量标记 |

### 导入批次 ImportBatch

| 字段 | 含义 |
|---|---|
| import_batch_id | 导入批次 ID |
| source_file | 来源文件名 |
| imported_at | 导入时间 |
| status | 导入状态 |
| record_count | 成功记录数 |
| warning_count | 警告数量 |
| error_count | 错误数量 |

### 质量问题 QualityIssue

| 字段 | 含义 |
|---|---|
| issue_id | 问题 ID |
| import_batch_id | 导入批次 ID |
| issue_type | 问题类型 |
| severity | 严重级别 |
| message | 中文说明 |
| source_file | 来源文件 |
| raw_sheet | 来源工作表 |
| raw_cell | 来源单元格 |
| plot_code | 关联地块编号 |
| metric_code | 关联指标编码 |

## 后续补充

正式接入 PostgreSQL + PostGIS 前，需要把以上概念模型细化为数据库表结构、索引、空间字段和迁移策略。
