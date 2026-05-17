# API 文档

## 设计原则

API 主线是“数字孪生场景查询”，不再提供 Excel 导入、导入报告或文件导出接口。所有接口默认使用当前演示场景 `demo-ricefield-2025`，支持可选 `scenario_id` 校验。

## 接口总览

| 接口 | 用途 |
|---|---|
| `GET /api/health` | 健康检查 |
| `GET /api/scenarios` | 场景列表 |
| `GET /api/scenarios/current` | 当前场景 |
| `GET /api/scenarios/{scenario_id}` | 场景详情 |
| `GET /api/scenarios/{scenario_id}/overview` | 场景驾驶舱数据 |
| `GET /api/metrics` | 指标字典 |
| `GET /api/plots` | 地块列表 |
| `GET /api/dates` | 可用观测日期 |
| `GET /api/map/layers` | Cesium 地块图层和指标着色 |
| `GET /api/plots/{plot_id}/summary` | 地块摘要 |
| `GET /api/plots/{plot_id}/series` | 地块趋势 |
| `GET /api/analysis/correlation` | 第一阶段占位相关性接口 |
| `GET /api/analysis/metric-compare` | 指标地块对比 |
| `GET /api/analysis/warnings` | 预警分析 |

已移除：

- `/api/imports`
- `/api/imports/{id}/report`
- `/api/export/report`

## 场景概览

`GET /api/scenarios/demo-ricefield-2025/overview`

返回：

```json
{
  "scenario": {
    "scenario_id": "demo-ricefield-2025",
    "scenario_name": "稻田数字孪生演示场景 2025",
    "data_mode": "demo"
  },
  "stat_cards": [
    {"label": "地块数量", "value": "8", "note": "程序生成示例地块"}
  ],
  "health_score": 92,
  "default_metric_code": "crop_growth",
  "default_observed_at": "2025-07-15",
  "quality_counts": {"normal": 3954, "missing": 2, "outlier": 4, "error": 0},
  "region_status": [
    {"region": "试验一区", "plot_count": 4, "warning_count": 3}
  ]
}
```

## 地图图层

`GET /api/map/layers?metric_code=crop_growth&observed_at=2025-07-15`

返回 GeoJSON FeatureCollection。每个 feature 的 `properties` 包含：

- `plot_id`
- `plot_code`
- `plot_name`
- `region`
- `metric_code`
- `value`
- `unit`
- `observed_at`
- `quality_flag`
- `fill_color`
- `batch_id`
- `data_source_id`

## 指标对比

`GET /api/analysis/metric-compare?metric_code=crop_growth&observed_at=2025-07-15`

返回按指标值排序的地块列表，字段包含 `rank`、`plot_id`、`plot_code`、`region`、`value`、`unit`、`quality_flag`。

## 预警分析

`GET /api/analysis/warnings`

返回缺失、异常和错误预警列表。每条预警包含地块、指标、日期、严重级别和值。

## 错误

不存在的场景、地块或指标返回 404，并使用中文错误：

```json
{"detail": "未找到场景：not-found"}
```
