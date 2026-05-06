# 指标字典

## 目标

所有指标进入系统前必须先进入指标字典。指标字典用于统一中文名称、编码、类别、单位、数值精度、正常范围、地图色阶和来源类型。

第一版指标字典已在后端代码中固化为 `backend/app/core/metric_dictionary.py`，数据结构由 `backend/app/schemas/data_model.py` 中的 `Metric` 和 `NormalRange` 约束。

## 字段定义

| 字段 | 含义 |
|---|---|
| `metric_code` | 指标编码，前后端、导入服务和分析模块统一使用 |
| `metric_name` | 中文名称 |
| `category` | 指标类别，如作物指标、土壤指标、土壤养分指标 |
| `unit` | 标准单位 |
| `value_type` | 数值类型，第一版限定为 `float` / `int` |
| `precision` | 展示和导出时建议保留的小数位数 |
| `normal_range` | 正常范围，包含 `min` 和 `max` |
| `color_scale` | 地图色阶，第一版使用 `red-yellow-green` 或 `green-yellow-red` |
| `description` | 指标说明 |
| `source_type` | 数据来源类型，第一版支持 `excel` / `geojson` / `manual` |

## 第一版指标

| metric_code | 中文名称 | 类别 | 单位 | 类型 | 精度 | 正常范围 | 色阶 | 来源 |
|---|---|---|---|---|---:|---|---|---|
| `crop_growth` | 作物长势 | 作物指标 | score | float | 2 | 0.6 - 1.0 | red-yellow-green | excel |
| `maturity_prediction` | 成熟期预测 | 作物指标 | 天 | int | 0 | 70 - 140 | green-yellow-red | excel |
| `chlorophyll` | 叶绿素 | 作物指标 | SPAD | float | 2 | 30 - 50 | red-yellow-green | excel |
| `nitrogen` | 氮 | 土壤养分指标 | mg/kg | float | 2 | 80 - 200 | red-yellow-green | excel |
| `phosphorus` | 磷 | 土壤养分指标 | mg/kg | float | 2 | 10 - 40 | red-yellow-green | excel |
| `potassium` | 钾 | 土壤养分指标 | mg/kg | float | 2 | 80 - 200 | red-yellow-green | excel |
| `ph` | pH | 土壤指标 | pH | float | 2 | 5.5 - 7.5 | red-yellow-green | excel |
| `organic_matter` | 有机质 | 土壤指标 | g/kg | float | 2 | 20 - 40 | red-yellow-green | excel |
| `soluble_total_salt` | 可溶性总盐分 | 土壤环境指标 | g/kg | float | 3 | 0 - 2 | green-yellow-red | excel |
| `leaf_area_index` | 叶面积指数 | 作物指标 | LAI | float | 2 | 3 - 7 | red-yellow-green | excel |
| `plant_height` | 株高 | 作物指标 | cm | float | 1 | 60 - 120 | red-yellow-green | excel |

## 治理规则

同一指标只能有一个稳定的 `metric_code`。如果 Excel 中出现同义字段、不同单位或不同写法，应在导入阶段映射到指标字典，并在质量报告中记录转换和异常情况。

第一版正常范围用于 MVP 数据校验、地图着色和异常提示的基准。后续拿到研究所确认的阈值后，应优先更新指标字典、测试和本文档，再调整导入质量规则。
