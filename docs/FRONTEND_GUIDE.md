# 前端开发指南

## 技术栈

目标前端栈为 Vue 3 + TypeScript + Vite + Tailwind CSS + shadcn-vue + Reka UI + ECharts + CesiumJS + Axios；Vue Router 与 Pinia 继续保留。Ant Design Vue 标记为待移除旧依赖，运行时代码尚未完全迁移前暂不删除依赖和全局注册。

## 目录约定

| 目录 | 说明 |
|---|---|
| `src/api` | 后端 API 请求 |
| `src/pages` | 六页数字孪生演示页面 |
| `src/components/ui` | shadcn-vue 源码组件层，保留接近上游的原子组件 |
| `src/components/base` | 通用布局、地图、图表、表格、筛选器和状态组件 |
| `src/components/workbench` | 迁移期遗留工作台组件，可被已迁移页面暂时引用，不作为新增基础组件目录 |
| `src/services` | 页面无关的转换、排序、状态计算 |
| `src/types` | API 和通用类型 |
| `src/types/table.ts` | 项目表格列配置类型，替代页面继续从 Ant Design Vue 导入 `TableColumnsType` |

## UI 组件迁移策略

- 新增或迁移页面优先使用 `src/components/base` 中的项目语义组件，不在页面内直接堆叠大量 `src/components/ui` 原子组件。
- `src/components/ui` 只存放 shadcn-vue 源码组件；需要调整业务语义、数据状态、地图图例、图表容器、表格操作等行为时，应封装到 `base` 层。
- 当前 `src/components/ui` 已补齐 `alert` 与 `toggle-group`，其中 `toggle-group` 依赖同目录 `toggle` 源码组件；不要为了后续页面假设批量新增组件。
- `src/components/base/AppShell.vue` 是主布局入口，`src/layouts/MainLayout.vue` 只负责包裹路由出口；后续页面迁移应优先接入 `base` 组件，而不是扩展 `workbench` 目录。
- Ant Design Vue 相关依赖、全局注册、主题配置和 `vendor-antd` 分包属于迁移期遗留项；本轮不删除依赖和入口。页面文件不得继续新增 `<a-*>` 控件，只有确认全局入口也无需保留后，才删除依赖。
- 本次 UI 栈迁移不改变后端 API、数据模型、模拟数据生成逻辑，不恢复文件导入能力，也不扩大六页 MVP 闭环。
- App Shell 与基础组件优先迁移：`AppHeader`、`AppSidebar`、`PageContainer`、`StatCard`、`ChartCard`、`StatusTag`、`MetricValueTag`、`FilterBar`、`DataTable`、基础选择器和加载/空状态组件使用 Tailwind CSS + shadcn-vue 风格实现。
- 状态展示统一走 `src/utils/status.ts`，前端只展示 `正常 / 关注 / 预警 / 严重 / 无数据`，不把后端 `missing / outlier / error` 等技术枚举作为用户文案。
- `DataTable` 不再使用 `a-table`，但继续兼容旧页面的 `columns`、`dataSource`、`bodyCell` slot、分页和横向滚动参数，避免一次性重写业务页面。
- 第二轮 base 组件迁移聚焦 `DataTable`、`FilterBar`、`ChartCard`、`StatCard`：这些组件内部使用 Tailwind CSS + shadcn-vue 源码组件或 `--rf-*` token，不再依赖 AntD DOM 结构。页面中仍直接存在的 `a-button`、`a-alert`、`a-tooltip`、`a-drawer`、`a-select`、`a-segmented` 属于后续逐页迁移范围。
- 第三轮页面级迁移已清理 `SystemDocsPage.vue`、`PlotDetailPage.vue`、`MetricComparePage.vue`、`WarningAnalysisPage.vue` 以及地图趋势组件中的 Ant Design Vue 控件标签：按钮、提示、抽屉、选择器、分段控件、Tooltip 与 skeleton 均改为 `base` 组件或 shadcn-vue 源码组件。`main.ts`、`App.vue`、`vite.config.ts`、`styles/theme.ts` 和依赖仍保留，作为后续全局入口清理前的兼容边界。

## 页面路由

- `/overview`
- `/map-twin`
- `/plot-detail/:plotId?`
- `/metric-compare`
- `/warnings`
- `/system-docs`

不再提供 `/data-import`、`/outliers`、`/correlation`。

## 页面结构与视觉规范

- 应用使用固定浅色左侧导航和顶部状态栏，导航当前项必须有清晰绿色高亮。
- 页面主体统一使用 `PageContainer`，页面标题、说明和操作区保持一致层级。
- 场景驾驶舱使用顶部程序化场景横幅承载场景编号、中文场景名、最近观测日期、地图入口和预警入口，避免营销化首页和真实来源不明图片。
- 场景驾驶舱首页应优先复用现有 `overview`、`metrics`、`metric-compare`、`plot-series` 和 `warnings` API，不为了视觉效果新增复杂后端逻辑。
- 场景驾驶舱核心结构固定为：场景横幅、5 个核心 KPI、关键指标概览、风险状态分布、区域状态、重点关注地块。
- Cesium 地图孪生页必须让地图成为首屏视觉中心，右侧详情和下方图表只作为辅助分析。
- 地块画像页使用 `PageContainer` 动态标题 `地块画像 / {plot_code}`，顶部横向摘要卡承载地块编号、状态、名称、区域、面积、品种、最近观测、来源和批次，再进入详情与趋势。
- 地块画像页采用三栏布局：左侧基础信息（260px）、中间指标快照网格（auto-fill）、右侧单指标趋势图（320px+）。底部三栏分别是观测批次表、预警建议面板和地块备注占位卡。
- 地块画像指标快照卡按指标字典固定优先展示 11 个核心指标：作物长势、叶绿素、氮、磷、钾、pH、有机质、盐分、LAI、株高、成熟期预测。卡片包含指标名称、当前值+单位、StatusTag、较上次观测变化（箭头+百分比），左边条颜色按状态等级区分；无数据时显示“暂无数据”。
- 趋势图支持指标选择下拉和近7/15/30天/全部时间范围切换，支持 markArea 显示指标正常范围。
- 预警与建议区域展示当前地块相关预警并附简洁建议措施，不编造过度具体的农艺处方。
- 观测批次记录使用 `DataTable`，字段为批次编号、观测日期、数据来源、观测指标数、数据质量、备注；演示数据只有单一批次编号时，可按观测日期聚合最近记录。
- 从地图页点击"查看画像"进入地块画像，"定位到地图"按钮回到 `/map-twin?plotId=xxx`；地图页读取查询参数后应尽量选中对应地块并刷新右侧详情。
- 指标对比页使用 `MetricComparePage.vue` 组织完整分析工作台：`FilterBar` 筛选指标、观测日期和区域；5 个 `StatCard` 展示地块总数、均值、最高值、最低值和异常地块数；主区域由地块排行图、区域对比卡和状态分布环图组成；底部使用 `DataTable` 展示明细数据和指标说明。
- 指标对比页默认优先展示叶绿素指标。区域对比、状态占比、较均值差值在前端基于 `/analysis/metric-compare` 返回列表聚合；较昨日变化、观测批次和数据来源通过现有 `/plots/{plot_id}/series` 补充，不新增 API 字段。
- 指标对比页排行图通过 `EChartView` 的 click 事件进入地块画像；明细表中“查看画像”跳转 `/plot-detail/:plotId?`，“定位地图”跳转 `/map-twin?plotId=xxx`。地图页继续复用现有 `plotId` 查询参数选中逻辑。
- 指标对比页空状态统一为：未找到指标、当前日期暂无观测数据、当前筛选下暂无对比数据；API 请求失败使用统一 `ErrorState`。
- 预警分析页使用 `WarningAnalysisPage.vue` 组织风险诊断中心：顶部 5 个 `StatCard`、`FilterBar` 筛选、左侧双环图、中部 `CesiumMapPanel` 预警地块分布、右侧最新预警列表和底部 `DataTable` 明细。
- 预警分析页前端基于现有 `/analysis/warnings` 与 `/map/layers` 数据聚合风险统计和地图着色，将 `missing / outlier / error` 语义映射为数据质量预警、农情状态预警、趋势变化预警以及关注/预警/严重等级，未新增 API 字段。
- 预警分析页点击最新预警或地图地块会同步选中地块、滚动到明细表并高亮对应行；明细表中“查看画像”跳转 `/plot-detail/:plotId?`，“定位地图”跳转 `/map-twin?plotId=xxx`，继续复用地图页已有 `plotId` 查询参数选中逻辑。
- 预警分析页风险描述和建议措施只做谨慎提示，不直接展示后端技术枚举，不编造具体农艺处方。
- 系统说明页聚焦平台定位、当前模拟数据、功能边界、后续演进和文档索引。
- 所有页面中文文案不得回到原始文件处理主线，不展示旧版文件处理或文件报告概念。

## API 使用

前端只请求标准化 API，不解析本地文件。新增页面应优先复用 `src/api/index.ts` 中的函数。

## 测试

当前服务层测试：

```powershell
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
```

构建：

```powershell
npm --prefix frontend run build
```
## Cesium 地图孪生组件与交互规则

- 页面入口：`/map-twin`，页面标题为 `Cesium 地图孪生`，副标题为 `地块空间分布、指标可视化与交互分析`。
- 页面组件：`MapAnalysisPage.vue` 组织工作台结构；`CesiumMapPanel.vue` 只负责 Cesium 容器、地块 polygon、中心编号、地图工具、图例插槽和图层开关响应。
- 筛选交互：指标、日期、区域、查询、重置放在地图顶部浮层。切换筛选项后可自动刷新图层，点击查询会按当前条件重新请求 `/api/map/layers`；重置回到叶绿素、最新日期和全部区域。
- 地块交互：点击 polygon 或地块编号后选中地块，右侧详情、当前指标、关键指标快照、趋势图、关键指标表和最新观测记录联动刷新。选中地块仅跳转画像，不提供编辑。
- 路由联动：从地块画像页进入 `/map-twin?plotId=xxx` 时，地图页初始化后读取 `plotId` 查询参数，加载图层后匹配地块并刷新详情；若当前图层中没有该地块，则保留地图页面并显示空详情状态。
- 趋势交互：趋势图基于 `/api/plots/{plot_id}/series` 返回的标准化时序数据，支持近 7 天、近 15 天、近 30 天切换；较昨日变化在前端由当前点和前一日点计算。
- 图层交互：图层控制使用项目语义开关组件，后续底层迁移为 shadcn-vue / Reka UI 实现；控制地块边界、当前指标渲染、预警地块高亮和区域边界。不得新增测距、绘制、编辑、上传、GeoJSON 导入等复杂 GIS 功能。
- 数据约束：地图页只消费标准化 API 和程序生成示例边界，不直接解析 Excel、GeoJSON、PDF、图片或真实客户数据文件。

## 预警分析组件与交互规则

- 页面入口：`/warnings`，页面标题为 `预警分析`，副标题为 `识别数据异常与农情风险，辅助科学决策。`
- 页面组件：`WarningAnalysisPage.vue` 复用 `StatCard`、`FilterBar`、`ChartCard`、`EChartView`、`CesiumMapPanel`、`StatusTag` 和 `DataTable`，不新增页面专用基础组件。
- 筛选逻辑：指标、区域和日期范围请求 `/api/analysis/warnings`；预警类型和严重程度在前端基于语义映射过滤。重置恢复全部指标、全部区域、全部类型、全部严重程度和空日期范围。
- 地图联动：页面用 `/api/map/layers` 返回的示例地块边界叠加当前筛选后的最严重预警等级，传入 `CesiumMapPanel` 渲染；预警页开启 `tightView` 紧凑视角以提升地块可见性；点击地块会选中对应预警并滚动到明细表。
- 列表联动：最新预警列表取当前筛选结果前 5 条，点击后同步 `selectedPlotId` 与 `selectedWarningId`；`DataTable` 通过 `rowClassName` 高亮当前预警行。
- 路由联动：`查看画像` 使用 `buildPlotDetailRequestPlan(plotId)` 跳转 `/plot-detail/:plotId?`；`定位地图` 使用 `buildMapTwinLocation(plotId)` 跳转 `/map-twin?plotId=xxx`。
- 数据边界：预警页不引入真实客户数据、文件上传或旧导入语义；如未来后端新增预警类型、处理状态或建议字段，必须同步更新 `docs/API.md`、`docs/DATA_MODEL.md`、schema 和测试。
