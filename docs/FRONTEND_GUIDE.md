# 前端开发指南

## 技术栈

Vue 3、TypeScript、Vite、Vue Router、Pinia、Ant Design Vue、ECharts、CesiumJS、Axios。

## 目录约定

| 目录 | 说明 |
|---|---|
| `src/api` | 后端 API 请求 |
| `src/pages` | 六页数字孪生演示页面 |
| `src/components/base` | 通用布局、地图、图表、表格、筛选器和状态组件 |
| `src/services` | 页面无关的转换、排序、状态计算 |
| `src/types` | API 和通用类型 |

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
- 地块画像页使用顶部地块概要承载地块编号、区域、最近观测、来源和批次，再进入详情与趋势。
- 指标对比页除排行图和表格外，应保留区域对比与状态分布，便于解释空间差异。
- 预警分析页统一使用 `normal`、`watch`、`warning`、`critical` 四级色阶，对应正常、关注、预警、严重。
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
- 趋势交互：趋势图基于 `/api/plots/{plot_id}/series` 返回的标准化时序数据，支持近 7 天、近 15 天、近 30 天切换；较昨日变化在前端由当前点和前一日点计算。
- 图层交互：图层控制使用 Ant Design Vue `a-switch`，控制地块边界、当前指标渲染、预警地块高亮和区域边界。不得新增测距、绘制、编辑、上传、GeoJSON 导入等复杂 GIS 功能。
- 数据约束：地图页只消费标准化 API 和程序生成示例边界，不直接解析 Excel、GeoJSON、PDF、图片或真实客户数据文件。
