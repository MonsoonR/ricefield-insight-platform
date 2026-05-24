# 变更记录

## 2026-05-22

### 修改

- 修正 `预警分析` 页面左侧环图图例拥挤问题：关闭窄卡片内 ECharts 侧边图例，改为图下方紧凑图例展示类型、数量和占比，避免文字压在圆环上。
- 优化预警地图初始视角，`CesiumMapPanel` 新增 `tightView` 紧凑视角参数，预警页地块在地图中占比更高，编号和风险色块更清晰。
- 按 `docs/design-reference/warnings-analysis-reference.png` 优化 `预警分析` 页面为“风险诊断中心”，形成顶部风险统计卡、紧凑筛选区、预警类型/严重程度分布、预警地块地图、最新预警列表和预警明细表。
- 预警分析页前端基于现有 `/analysis/warnings` 与 `/map/layers` 数据聚合风险总览、受影响地块、受影响指标和地图严重程度着色，未新增后端 API 字段。
- 将 `missing / outlier / error` 等技术字段转换为数据质量预警、农情状态预警、趋势变化预警以及关注/预警/严重等级，补充面向用户的中文预警描述和谨慎建议措施。
- 最新预警列表、地图地块和明细表新增联动：点击预警或地块会选中对应地块、滚动到明细表并高亮对应行；“查看画像”和“定位地图”分别联动地块画像与地图孪生。
- `DataTable` 新增 `rowClassName` 透传能力，并统一表格单元格不换行，支持预警明细表横向滚动和行高亮。
- 按 `docs/design-reference/metric-compare-reference.png` 优化 `指标对比` 页面为多维度指标分析工作台，形成紧凑筛选区、5 个统计卡、地块排行图、区域对比、状态分布、明细数据表和指标说明。
- 指标对比页默认优先展示叶绿素指标；查询/重置按钮遵循统一 `FilterBar` 交互，筛选区显示当前参与对比地块数量。
- 地块排行图按指标值排序，使用正常、关注、预警、严重四级状态色，并新增均值参考线和柱子点击进入地块画像能力。
- 区域对比、状态分布、较均值差值在前端基于现有对比列表聚合；较昨日变化、观测批次和数据来源复用现有地块时序接口补充，未新增后端 API 字段。
- 明细表补齐排名、地块编号、地块名称、区域、当前指标值、较均值差值、较昨日变化、状态、数据来源、观测批次和操作列；“查看画像”和“定位地图”分别联动地块画像与地图孪生。
- `EChartView` 新增通用 click 事件透传，供排行图等图表联动使用。

### 文档更新

- 更新 `docs/DESIGN_SYSTEM.md`，补充预警分析页环图图例不得挤压圆环、预警地图应使用紧凑初始视角的规范。
- 更新 `docs/FRONTEND_GUIDE.md`，补充预警页 `CesiumMapPanel` `tightView` 使用说明。
- 更新 `docs/DESIGN_SYSTEM.md`，新增第 13 章“预警分析页面规范”，补充风险统计卡、筛选区、双环图、预警地图、最新预警、明细表、严重程度颜色、语义映射、建议措施和空状态规范。
- 更新 `docs/FRONTEND_GUIDE.md`，补充预警分析页组件结构、筛选逻辑、前端语义映射、地图/列表/表格联动和路由跳转说明。
- 更新 `docs/USER_MANUAL.md`，补充预警分析页筛选风险、查看分布、点击地图、查看最新预警、进入地块画像和定位地图的操作说明。
- 更新 `docs/DESIGN_SYSTEM.md`，新增第 12 章“指标对比页面规范”，补充筛选、KPI、排行图、区域对比卡、状态分布图、明细表、指标说明和空状态规范。
- 更新 `docs/FRONTEND_GUIDE.md`，补充指标对比页组件结构、前端聚合逻辑、时序补充数据和页面联动说明。
- 更新 `docs/USER_MANUAL.md`，补充指标对比页筛选、排行、区域对比、状态分布、明细表、地块画像和地图定位操作说明。

### 验证

- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q`（19 passed）。
- 已通过前端服务测试：`test:overview`、`test:page-linkage`、`test:twin-analysis`、`test:map`。
- 已通过前端构建：`npm --prefix frontend run build`（构建成功；保留既有 Cesium/Ant Design 大 chunk 提示）。
- 已通过 Playwright 截图验证：`/warnings` 桌面与移动视口渲染正常，风险统计、筛选区、分布图、地图、最新预警和明细表布局可用。
- 已通过 Playwright 截图验证：`/metric-compare` 桌面与移动视口渲染正常，无框架错误页；`/plot-detail/demo-ricefield-2025-B04` 和 `/map-twin?plotId=demo-ricefield-2025-B04` 可正常加载联动目标页。

## 2026-05-21

### 修改

- 按参考图继续优化 `地块画像` 页面：新增动态标题 `地块画像 / {plot_code}`，顶部摘要卡改为横向身份区 + 分隔信息列 + 定位按钮，桌面端保持基础信息 / 指标快照 / 趋势图三栏档案布局。
- 指标快照按指标字典固定展示 11 个核心指标，并对缺失指标显示“暂无数据”；趋势时间范围改为基于当前地块最新观测日期计算，避免近 7/15/30 天在演示历史数据上误判为空。
- 观测批次记录改为基于时序点按观测日期与批次聚合，保留真实批次编号，同时展示最近观测日期、来源、指标数、质量状态和备注。
- 地图页新增读取 `/map-twin?plotId=xxx` 查询参数的初始化联动，画像页“定位到地图”可回到地图并尽量选中当前地块。
- 重构地块画像页（`PlotDetailPage.vue`）为"单地块数字档案"设计：顶部摘要卡（大号编号 + 状态 + 元信息 + 定位到地图）、三栏主体（基础信息 / 指标快照网格 / 单指标趋势图）、底部观测批次表 + 预警与建议面板。
- 指标快照卡新增较上次变化百分比（箭头 + 涨跌色）和左侧 3px 状态色条。
- 趋势图支持指标选择下拉 + 时间范围（近7/15/30天/全部）切换，支持 markArea 显示正常区间。
- 新增预警与建议面板，展示地块相关预警列表及谨慎建议措施。
- 基础信息卡新增面积、品种、播种/插秧/成熟期模拟字段（标注"模拟"），不伪装真实数据。

### 文档更新

- 更新 `docs/DESIGN_SYSTEM.md`，新增第 11 章"地块画像页面规范"（摘要卡、三栏布局、指标快照卡、趋势图、预警建议、模拟字段规则、联动规则）。
- 更新 `docs/FRONTEND_GUIDE.md`，补充地块画像页的三栏布局、指标快照卡结构、趋势图交互和页面联动说明。
- 更新 `docs/USER_MANUAL.md`，补充地块画像页用户操作说明（摘要卡、指标快照、趋势切换、观测批次、预警建议、返回地图联动）。
- 同步修正 `docs/DESIGN_SYSTEM.md` 旧版“地块画像含地图定位栏”表述，明确当前页为摘要卡、三栏主体、底部批次/预警/备注结构。

### 验证

- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q`（19 passed）。
- 已通过前端服务测试：`test:overview`、`test:page-linkage`、`test:twin-analysis`、`test:map`。
- 已通过前端构建：`npm --prefix frontend run build`（构建成功；保留既有 Cesium/Ant Design 大 chunk 提示）。
- 已通过 Playwright 页面检查：`/plot-detail/demo-ricefield-2025-A04` 桌面视口渲染正常，控制台 0 error / 4 warning（均为现有前端依赖提示）。

## 2026-05-20

### 修改

- 优化 `Cesium 地图孪生` 页面为核心空间分析工作台，形成地图主区域、右侧地块详情、下方趋势图、关键指标表和最新观测记录的结构。
- 将地图筛选栏调整为地图顶部浮层，包含指标选择、日期选择、区域选择、查询和重置；查询按钮使用主绿色，重置按钮使用浅色描边。
- 强化 Cesium 地块渲染，新增地块中心编号、选中地块亮色描边和弱发光、缺失数据灰色低透明度、预警地块高亮，以及地图左下角指标色阶图例。
- 优化地图工具，新增定位选中地块、图层透明度、回到默认视角、放大和缩小按钮，统一白底圆角和轻阴影样式。
- 扩展右侧地块详情面板，展示状态、地块编号、区域、名称、面积、演示品种、最近观测、数据来源、观测批次、当前指标、较昨日变化和关键指标快照。
- 新增图层控制开关，支持地块边界、当前指标渲染、预警地块和区域边界显示控制；未新增 GeoJSON 导入、文件上传、地块编辑、测距或绘制功能。

### 文档更新

- 更新 `docs/DESIGN_SYSTEM.md`，补充 Cesium 地图孪生页面视觉规范。
- 更新 `docs/FRONTEND_GUIDE.md`，补充地图页组件分工、筛选、地块点击、趋势和图层交互规则。
- 更新 `docs/USER_MANUAL.md`，同步地图页用户可见操作说明。

### 验证

- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。
- 已通过前端服务测试：`npm --prefix frontend run test:overview`、`npm --prefix frontend run test:page-linkage`、`npm --prefix frontend run test:twin-analysis`、`npm --prefix frontend run test:map`。
- 已通过前端构建：`npm --prefix frontend run build`。

## 2026-05-19

### 修改

- 第二阶段优化场景驾驶舱首页，形成程序化稻田场景横幅、5 个核心 KPI、关键指标概览、风险状态分布、区域状态和重点关注地块的驾驶舱结构。
- 首页关键指标概览复用现有 `metrics`、`metric-compare` 和 `plot-series` API，展示作物长势、叶绿素、氮、pH、LAI 的最新值、单位、近 7 次趋势和状态；未新增后端字段。
- 首页交互补齐：重点关注地块跳转地块画像，预警入口跳转预警分析，地图入口跳转 Cesium 地图孪生。
- 前端状态映射补充直接识别 `watch` 和 `warning` 状态值，确保概览页四级状态标签与设计系统一致。
- 前端入口页新增内联 SVG favicon，避免本地浏览器自动请求 `/favicon.ico` 产生 404 控制台错误。
- 重构前端整体视觉风格，统一为浅色科研工作台与绿色稻田数字孪生平台风格。
- 左侧导航改为浅色固定侧栏，当前页面使用绿色高亮；顶部栏改为全局状态、预警入口、文档入口和演示用户信息。
- 优化基础组件样式，统一 `PageContainer`、`FilterBar`、`StatCard`、`ChartCard`、`DataTable`、`StatusTag`、`MetricValueTag` 和 `CesiumMapPanel` 的间距、圆角、阴影、标题和预警色阶。
- 优化场景驾驶舱，新增更强的平台场景横幅与健康度展示，并统一区域预警、质量分布、指标排行和近期预警视觉。
- 优化 Cesium 地图孪生页，提升地图高度和视觉权重，统一地图图例、详情面板、趋势图和筛选摘要。
- 优化地块画像页，新增地块概要区，强化地块编号、区域、最近观测、数据来源、观测批次和完整率展示。
- 优化指标对比页，新增区域对比和状态分布，排行图按质量状态使用统一色阶。
- 优化预警分析页，统一图例与状态分级颜色，强化预警地块分布和地块状态信息。
- 优化系统说明页，聚焦平台定位、当前模拟数据、数字孪生构建流程、系统边界、后续演进和文档索引。
- 收敛第一阶段基础设计系统，统一状态分级命名为 `normal`、`watch`、`warning`、`critical`，并清理前端残留的旧平台提示文案。
- 完整补充 `docs/DESIGN_SYSTEM.md` 长期规范，覆盖平台视觉定位、色彩、布局、组件、图表、地图、文案和后续约束，作为后续页面开发的统一基线。

### 文档更新

- 更新 `docs/DESIGN_SYSTEM.md`，补充第二阶段场景驾驶舱横幅、KPI、关键指标、风险分布、区域状态和重点关注地块规范。
- 更新 `docs/FRONTEND_GUIDE.md`，明确场景驾驶舱首页结构和 API 复用原则。
- 更新 `docs/USER_MANUAL.md`，同步场景驾驶舱第二阶段首页使用说明。
- 更新 `docs/DESIGN_SYSTEM.md`，沉淀参考图提炼出的平台色彩、布局、组件、地图和预警规范。
- 更新 `docs/FRONTEND_GUIDE.md`，补充六页页面结构和视觉实现规则。
- 更新 `docs/USER_MANUAL.md`，同步新版页面功能说明和状态分级说明。

### 验证

- 已通过场景驾驶舱浏览器验证：`http://127.0.0.1:5173/overview` 桌面与移动视口渲染正常，控制台 0 error / 0 warning；重点关注地块、预警入口和地图入口跳转正常。
- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。
- 已通过前端服务测试：`npm --prefix frontend run test:overview`、`npm --prefix frontend run test:page-linkage`、`npm --prefix frontend run test:twin-analysis`、`npm --prefix frontend run test:map`。
- 已通过前端构建：`npm --prefix frontend run build`。
- 本地服务检查：已有后端 `http://127.0.0.1:8000/api/health` 返回 200；前端开发服务可通过 `http://127.0.0.1:5174/overview` 访问。

## 2026-05-18

### 新增

- 新增 `docs/CLAUDE_WORKFLOW.md`，明确当前阶段全程优先使用 Claude 开发，统一在 `claude/digital-twin-dev` 分支上工作，并规定任务前后检查清单、验证命令、文档同步规则、Git commit 规则、push 规则与最终回复格式。

### 修改

- `docs/CODEX_WORKFLOW.md` 顶部加入"当前阶段说明"，说明当前阶段 Codex 暂停使用、日常开发改用 Claude；同时去除将"大创答辩 PPT"作为核心开发任务的措辞，明确当前主线是把系统功能和工程结构做扎实，大创答辩保留为后续展示场景。
- `README.md` 文档入口表加入 `docs/CLAUDE_WORKFLOW.md` 与 `docs/CODEX_WORKFLOW.md`，新增"开发协作"段落，指引使用 Claude 工作流和 `claude/digital-twin-dev` 分支。

### 删除

- 删除 `docs/dachuang-pitch/` 下答辩材料（README.md、index.html、立项答辩 PPT），不再作为仓库内长期产出。

### 验证

- 本次为纯文档修改，不涉及后端代码、前端代码、依赖、配置或数据契约，跳过完整前后端测试与构建。

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
