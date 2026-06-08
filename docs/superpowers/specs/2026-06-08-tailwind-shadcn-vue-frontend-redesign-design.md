# Tailwind + shadcn-vue 前端整体重构设计

## 背景

当前前端已经完成第一阶段六页 MVP 闭环，但整体观感仍偏通用后台模板，和期望中的“稻田数字孪生科研 GIS 工作台”存在明显差距。继续在 Ant Design Vue 上做局部皮肤调整，难以彻底摆脱默认控件、卡片和后台布局气质。

本次设计确认将前端重构方向调整为：完全移除 Ant Design Vue，转向 Tailwind CSS + shadcn-vue 源码组件体系。Vue 3、TypeScript、Vite、Vue Router、Pinia、Axios、ECharts 和 CesiumJS 继续保留。

## 目标

1. 建立统一的科研 GIS 工作台视觉系统。
2. 让地图成为首页和地图页的第一视觉主画布。
3. 以右侧 Inspector 承载选中地块画像、指标状态、趋势摘要和质量追溯。
4. 六个页面使用同一套 App Shell、命令栏、筛选器、表格、图表、状态标签和数据面板组件。
5. 保持项目第一阶段边界，不新增导入中心、权限系统、自动报告、多项目管理或复杂空间分析。

## 非目标

1. 不做答辩脚本和演示材料。
2. 不做 Docker Compose + Nginx 部署配置。
3. 不接入真实客户数据。
4. 不恢复 Excel、GeoJSON、PDF、图片等文件导入能力。
5. 不把项目迁移到 React 或 Next.js。
6. 不引入独立大屏系统或营销化首页。

## 技术决策

### 移除

- `ant-design-vue`
- Ant Design Vue 全局主题配置
- 依赖 Ant Design Vue 组件结构的页面实现

### 引入

- Tailwind CSS
- shadcn-vue
- Reka UI 相关无样式交互基础组件
- shadcn-vue 推荐的 `cn` 工具链和 CSS 变量体系
- Vue 生态图标方案，优先使用 `lucide-vue-next`

### 保留

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Axios
- ECharts
- CesiumJS

## 视觉方向

确认采用“稻田孪生场景感”的科研 GIS 工作台风格。

具体要求：

- 主基调为浅色科研工作台，不做深色大屏。
- 左侧使用窄导航，不做厚重后台侧栏。
- 顶部为命令栏，收敛场景、指标、日期、区域和状态入口。
- 首页和地图页采用地图主画布 + 右侧 Inspector。
- 地图区域需要有农业数字孪生识别度：稻田色彩、地块边界、图层控件、比例尺、质量图例和选中态。
- Cesium 底图不可用时不能黑屏，必须有可信的视觉兜底。
- 页面避免大横幅 hero、大号营销统计卡、过度渐变和重复卡片墙。

## 信息架构

### App Shell

App Shell 包含：

- 左侧窄导航；
- 顶部命令栏；
- 主内容画布；
- 可选右侧 Inspector；
- 页面级 loading、error、empty 状态。

左侧导航只承载页面切换和辅助入口，不承载复杂业务筛选。顶部命令栏负责统一放置场景、指标、日期、区域、类型等筛选控制。

### 地图主画布

地图主画布是首页和 Cesium 地图孪生页的核心组件。它必须支持：

- 地块边界；
- 指标着色；
- 地块编号；
- 选中态；
- 图层控制；
- 地图工具按钮；
- 质量状态图例；
- 比例尺与坐标信息；
- 底图失败兜底视觉。

### Inspector

Inspector 是右侧固定信息面板，用于展示当前选中对象。首页和地图页默认展示选中地块；其他页面可根据上下文展示指标、预警或文档摘要。

Inspector 内容优先级：

1. 对象身份：地块编号、名称、区域、状态。
2. 当前指标：指标名、值、单位、日期、质量标记。
3. 快照摘要：关键指标、健康度或质量计数。
4. 趋势摘要：小型趋势图或最近变化。
5. 追溯入口：`batch_id`、`data_source_id`、质量问题入口。

## 组件体系

优先通过 shadcn-vue CLI 添加或生成基础组件，再按项目设计系统定制。组件源码进入项目后属于本项目代码，允许按稻田 GIS 工作台需求维护。

第一批组件：

- Button
- Badge
- Card 或 Panel
- Select
- Tabs
- Table
- Tooltip
- Popover
- Dialog 或 Sheet
- Skeleton
- Separator
- ScrollArea

项目自建业务组件：

- AppShell
- AppSidebar
- CommandBar
- TwinMapPanel
- InspectorPanel
- FilterGroup
- StatusBadge
- MetricValue
- ChartPanel
- DataTable
- EmptyState
- ErrorState
- LoadingState

状态颜色全站固定：

| 状态 | 语义 | 用途 |
|---|---|---|
| `normal` | 正常 | 正常观测、正常地块 |
| `missing` | 缺失值 | 缺失观测和质量核验 |
| `outlier` | 异常值 | 异常观测和质量核验 |
| `error` | 错误记录 | 解析、匹配或转换链路问题 |
| `no_data` | 无匹配数据 | 没有观测记录，不等同于缺失 |

## 六页落地规则

### 场景驾驶舱

定位为第一入口。采用地图主画布 + 右侧场景 Inspector + 底部关键状态带。

重点回答：

- 当前数字孪生场景是什么；
- 默认指标和日期是什么；
- 地块整体状态如何；
- 哪些区域或地块需要关注。

### Cesium 地图孪生

定位为核心分析页。地图占比最大，筛选器更完整。

重点能力：

- 指标、日期、区域筛选；
- 地块点击；
- URL 参数定位；
- 地图与 Inspector 联动；
- 地图到地块画像跳转。

### 地块画像

定位为单地块详情页。不重复做大地图，重点展示地块身份、11 项指标快照、趋势、来源追溯和质量核验建议。

### 指标对比

定位为指标横向分析页。表格和图表并重，避免统计卡片墙。

内容包括：

- 当前筛选器；
- 指标排名表；
- 区域对比；
- 状态分布；
- 均值、极值、异常地块数等轻量派生结果。

### 预警分析

定位为质量问题工作台。突出缺失、异常、错误的核验流程。

要求：

- 保留地图定位；
- 预警列表按时间倒序；
- 建议文案只做数据质量核验；
- 不输出施肥、灌溉、用药等农艺处方。

### 系统说明

定位为产品内帮助中心。保持同一 App Shell，但降低视觉强度，不做营销介绍页。

## 实施顺序

1. 初始化 Tailwind CSS 与 shadcn-vue。
2. 建立 CSS 变量、Tailwind tokens 和 `cn` 工具。
3. 引入第一批 shadcn-vue 基础组件。
4. 替换 Ant Design Vue 全局入口和主题配置。
5. 重建 AppShell、AppSidebar、CommandBar。
6. 重建基础状态组件：Loading、Error、Empty、StatusBadge。
7. 重建地图面板与 Inspector。
8. 重构首页和 Cesium 地图孪生页。
9. 重构地块画像、指标对比、预警分析、系统说明。
10. 移除 Ant Design Vue 依赖和残留样式。
11. 更新技术栈文档、设计系统、前端指南、用户手册和变更记录。
12. 运行前端服务测试、构建和浏览器视觉验收。

## 验证策略

每轮前端实际代码修改后至少运行：

```powershell
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
npm --prefix frontend run build
```

重构首页和地图页时，还需要浏览器检查：

- `/overview`
- `/map-twin`
- `/map-twin?plotId=demo-ricefield-2025-A01`
- 桌面视口；
- 窄屏视口；
- 地块点击；
- 筛选联动；
- 地图兜底渲染；
- 文字和按钮不溢出。

## 风险与控制

| 风险 | 控制方式 |
|---|---|
| 技术栈切换导致一次性改动过大 | 按 App Shell、组件、页面分阶段提交 |
| shadcn-vue 组件默认风格仍偏通用 | 用项目 tokens 和业务组件统一农业 GIS 风格 |
| 移除 Ant Design Vue 影响表格和选择器 | 先建立 DataTable、Select、FilterGroup 的替代组件 |
| Cesium 地图与 Tailwind 布局冲突 | 地图容器使用稳定尺寸、min-height 和 overflow 边界 |
| 六页重构后接口联动回归 | 保留现有服务测试，并补充浏览器路径检查 |

## 用户确认结论

已确认：

- 答辩材料暂缓；
- Docker Compose + Nginx 有必要，但不在本轮优先级；
- MVP 演示验收不急；
- 当前前端观感与期望差距较大，应先继续优化前端；
- 前端整体方向为科研 GIS 工作台；
- 首屏骨架采用地图主画布 + 右侧 Inspector；
- 视觉气质采用稻田孪生场景感；
- 重构范围覆盖六页；
- 工程路线为先统一 App Shell 和组件系统；
- 完全舍弃 Ant Design Vue；
- 转向 Tailwind CSS + shadcn-vue。
