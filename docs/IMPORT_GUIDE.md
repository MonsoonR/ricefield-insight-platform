# 数据导入指南

## 目标

数据导入的目标不是简单读取文件，而是把来源不统一的 Excel 和 GeoJSON 转换为稳定、可追溯、可检查的标准化数据。

第一版已实现 Excel 和地块 GeoJSON 的基础解析：Excel 读取 `.xlsx` 文件，把每个指标单元格转换为统一长表记录，并同步生成导入质量报告；GeoJSON 读取 `data/geojson/` 下的地块边界文件，输出标准化 `Plot` 列表、别名表和地块匹配报告。

## 第一版 Excel 导入流程

1. 接收或读取 `.xlsx` 文件，默认可从 `data/imports/` 目录批量读取。
2. 使用 `pandas` 通过 `openpyxl` 引擎读取所有工作表。
3. 校验工作表是否包含 `plot_code` 和 `observed_at` 两个必填列。
4. 将表头中命中指标字典的列识别为指标列，例如 `crop_growth`、`plant_height`。
5. 根据外部传入的地块映射表把 `plot_code` 匹配为 `plot_id`。
6. 将每个指标单元格转换为一条 `MetricObservation` 长表记录。
7. 根据指标字典中的单位、数值类型、精度和正常范围补齐标准字段并标记质量状态。
8. 生成 `ImportQualityReport`，所有缺失值、异常值、未匹配地块和错误单元格都必须进入报告。

## 第一版 Excel 输入格式

第一版支持两种 Excel 输入格式，统一输出为 `MetricObservation` 长表。

### 标准宽表模板

标准宽表适合后续整理后的导入模板。一个工作表至少包含：

| 字段 | 必填 | 说明 |
|---|---|---|
| `plot_code` | 是 | Excel 中的地块编号，用于匹配系统地块 |
| `observed_at` | 是 | 观测日期，可被解析为日期 |
| 指标编码列 | 是 | 列名必须是指标字典中的 `metric_code` |

示例：

| plot_code | observed_at | crop_growth | plant_height |
|---|---|---:|---:|
| P001 | 2026-05-01 | 0.82 | 82 |
| P002 | 2026-05-01 | 0.74 | 95 |

一个文件可以包含多个工作表，一个工作表可以包含一个或多个指标列。非指标字典列第一版不参与解析。

## 第一版 GeoJSON 导入流程

1. 默认读取 `data/geojson/` 目录下的 `.geojson` 文件。
2. 每个 Feature 从 `properties.plot_code`、`properties.id`、`properties.name`、`properties.编号` 或 `properties.地块编号` 中识别地块编号。
3. 从文件名、FeatureCollection `name` 或 Feature `properties.region` 推断区域；`east` / `东区` 归为东区，`west` / `西区` 归为西区。
4. 读取 Feature `geometry` 原样写入 `Plot.geometry`，供后续地图接口和 Cesium 展示使用。
5. 生成标准 `plot_code`、`plot_id`、`aliases`、`region`、`geometry`、`status`。
6. 生成 `plot_aliases` 别名表，支持一个别名映射到多个地块 ID，用于处理东区、西区同号地块或重复数据。
7. 可选传入 Excel 中出现过的地块编号，输出 Excel/GeoJSON 双向不匹配报告。

## 地块编号标准化规则

第一版标准化函数为 `normalize_plot_code(...)`，规则保持可解释、可回溯，不对无法确认的编号做强行猜测：

- 去除首尾空白、引号和花括号；
- 使用 Unicode NFKC 规范化，统一全角/半角字符；
- 删除编号内部空白，统一大小写；
- 将中文破折号、长短横线和下划线统一为 `-`；
- `21A-1` 这类“字母地块 + 分株后缀”归一为 `21A`，但 `E1-16`、`1-16` 这类基础编号保持不变；
- `64A/64C`、`21A/C`、`24-1C/1A` 这类复合写法会展开为多个别名；
- 东区、西区不靠 `plot_code` 合并，`plot_id` 使用区域前缀区分，例如 `east-21A` 与 `west-21A`；
- 疑似乱码编号，如包含替换字符 `�` 或常见 mojibake 片段的编号，进入 `garbled_plot_codes` 报告，不生成可定位地块；
- 同一区域内重复的标准编号进入 `duplicate_plot_codes`，对应地块状态标记为 `duplicate`；
- Excel 中存在但 GeoJSON 中无法定位的编号进入 `unmatched_excel_plots`；
- GeoJSON 中存在但当前 Excel 暂无数据的地块进入 `geojson_plots_without_excel_data`，对应地块状态标记为 `no_data`。

### 研究数据导出格式

当前 `data/imports/` 示例 Excel 使用研究数据导出格式，表头通常为：

| type | 地块 | 时间 | data | ... |
|---|---|---|---|---|
| 11 | baicheng-dong | 2025-10-03 | `"17C":"0.33"` | `S18:"0.26"` |

解析规则：

- `type` 映射为指标编码；
- `时间` 映射为 `observed_at`；
- 从第 4 列开始，每个非空单元格按 `地块编号:"数值"` 拆成一条观测记录；
- 单元格坐标作为 `raw_cell` 保留，例如 `D2`；
- `地块` 列暂作为来源区域信息保留在原始文件中，第一版不写入观测记录。

第一版 `type` 映射：

| type | metric_code |
|---|---|
| `11` | `crop_growth` |
| `16` | `maturity_prediction` |
| `43` | `chlorophyll` |
| `131` | `nitrogen` |
| `132` | `phosphorus` |
| `133` | `potassium` |
| `134` | `ph` |
| `135` | `organic_matter` |
| `136` | `soluble_total_salt` |
| `434` | `leaf_area_index` |
| `435` | `plant_height` |

## 质量标记规则

| 标记 | 触发条件 |
|---|---|
| `normal` | 地块、日期和指标值均可解析，且指标值位于指标字典正常范围内 |
| `missing` | 指标单元格为空，仍生成观测记录，`value` 为 `null` |
| `outlier` | 指标值可解析，但低于或高于指标字典 `normal_range` |
| `error` | 指标单元格存在但无法按指标类型解析，仍生成观测记录，`value` 为 `null` |

以下情况不会生成观测记录，但必须进入质量报告：

- `plot_code` 缺失；
- `plot_code` 无法匹配系统地块；
- `observed_at` 缺失或无法解析；
- 工作表缺少当前格式要求的必填列；
- 标准宽表没有可识别的指标列；
- 研究数据导出格式中的 `type` 无法映射指标；
- 研究数据导出格式中的 `地块编号:"数值"` 单元格无法拆解；
- Excel 文件无法读取。

## 质量报告结构

`ImportQualityReport` 至少包含：

| 字段 | 类型 | 说明 |
|---|---|---|
| `import_batch_id` | str | 导入批次 ID |
| `source_file` | str | 文件名称 |
| `successful_record_count` | int | 成功记录数，即 `quality_flag=normal` 的记录数 |
| `missing_value_count` | int | 缺失值数量 |
| `outlier_count` | int | 异常值数量 |
| `unmatched_plots` | list[str] | 未匹配地块编号列表 |
| `error_cells` | list[str] | 错误单元格列表，如 `B5`、`C6` |
| `skipped_record_count` | int | 因地块、日期或工作表结构问题跳过的指标单元格数量 |
| `parse_duration_ms` | int | 解析耗时，单位毫秒 |
| `status` | `success` / `partial` / `failed` | 导入状态 |
| `parse_errors` | list[str] | 工作表级或文件级解析错误说明 |

状态判定：

- `success`：生成记录且没有缺失、异常、错误、未匹配或跳过记录；
- `partial`：生成了部分记录，但存在质量问题；
- `failed`：文件无法读取，或没有生成任何观测记录。

## GeoJSON 报告结构

`PlotGeoJsonReport` 至少包含：

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_files` | list[str] | 已读取的 GeoJSON 文件 |
| `total_feature_count` | int | Feature 总数 |
| `parsed_plot_count` | int | 成功解析出的地块数量 |
| `duplicate_plot_codes` | list[str] | 同一区域内重复编号 |
| `garbled_plot_codes` | list[str] | 疑似乱码编号 |
| `unmatched_excel_plots` | list[str] | Excel 中存在但 GeoJSON 中无法定位的地块 |
| `geojson_plots_without_excel_data` | list[str] | GeoJSON 中存在但当前 Excel 暂无数据的地块 |

## 临时样例数据处理

开发早期可以使用临时样例数据理解真实文件结构，但临时目录不作为长期工程内容。样例数据后续可删除，因此业务代码、测试和正式文档不能硬编码临时样例目录路径。

如果当前没有真实 Excel 文件，使用 `backend/tests/fixtures/excel_fixtures.py` 生成最小 `.xlsx` 测试夹具来验证解析流程。GeoJSON 测试使用 `backend/tests/fixtures/geojson/` 下的最小静态夹具。测试夹具只表达稳定的导入契约，不依赖临时样例目录。

## 当前状态

已实现第一版 Excel 解析服务：

- 代码入口：`backend/app/services/importer/excel.py`；
- 单文件解析：`parse_excel_file(...)`；
- 目录批量解析：`parse_excel_directory(...)`，可读取传入的 `data/imports/` 目录；
- 测试：`backend/tests/test_excel_importer.py`，覆盖标准宽表和研究数据导出格式。

已实现第一版 GeoJSON 解析服务：

- 代码入口：`backend/app/services/importer/geojson.py`；
- 目录批量解析：`parse_geojson_directory(...)`，可读取传入的 `data/geojson/` 目录；
- 标准化函数：`normalize_plot_code(...)`；
- 别名映射：`build_plot_lookup(...)` 可把多个别名映射到同一 `plot_id`；
- 测试：`backend/tests/test_geojson_importer.py`，覆盖标准化、别名展开、区域区分、重复编号、乱码编号和 Excel/GeoJSON 双向未匹配报告。
