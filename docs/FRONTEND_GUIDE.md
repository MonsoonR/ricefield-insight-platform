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
- 场景驾驶舱使用顶部场景横幅承载当前场景和健康度，避免营销化首页。
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
