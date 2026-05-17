# 变更记录

## 2026-05-17

### 新增

- 新增数字孪生场景概览接口 `GET /api/scenarios/{scenario_id}/overview`。
- 新增指标对比接口 `GET /api/analysis/metric-compare`。
- 新增预警分析接口 `GET /api/analysis/warnings`。
- 新增前端“预警分析”页面和 `twinAnalysis` 服务测试。
- 新增大创立项答辩可编辑 PowerPoint：`docs/dachuang-pitch/稻田智研平台立项答辩-张焱哲.pptx`，包含 9 页答辩内容和演讲者备注。

### 修改

- 将项目主线从数据导入/质量报告平台重构为大创答辩用稻田数字孪生可视化平台。
- 前端导航调整为六页闭环：场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析、系统说明。
- 后端数据模型从 `ImportBatch` / `ImportQualityReport` 语义迁移为 `ObservationBatch` / `DataQualityIssue`。
- 地图、趋势、地块摘要响应不再暴露 Excel 来源文件、工作表或单元格字段。
- `README.md` 和 docs 文档全部更新为新版执行基准。
- 同步更新 `docs/dachuang-pitch/` 与 `docs/superpowers/specs/` 历史材料，避免继续引用旧版导入型 MVP。
- 更新 `docs/dachuang-pitch/README.md`，补充可编辑 PowerPoint 版本说明。

### 删除

- 删除 Excel importer、GeoJSON importer、数据库导入服务和相关测试夹具。
- 删除前端数据导入中心、导入状态组件、导入 API、导入服务和导入测试。
- 删除前端相关性页面和异常识别占位页面，改为预警分析页。
- 移除 `/api/imports`、`/api/imports/{id}/report`、`/api/export/report` 第一阶段接口。
- 后端依赖移除 `pandas` 和 `openpyxl`。

### 验证

- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。
- 已通过前端服务测试：`test:overview`、`test:page-linkage`、`test:twin-analysis`、`test:map`。
- 已通过前端构建：`npm --prefix frontend run build`。
- 已通过答辩 PPT 导出与校验：9 页幻灯片、9 组演讲者备注、无空媒体文件，布局检查 0 error / 0 warning。
