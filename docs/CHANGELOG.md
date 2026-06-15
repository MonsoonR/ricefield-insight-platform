# 变更记录

## 2026-06-15

### 修改

- 补齐前端设计 token：在 `global.css` 中落地 `--rf-status-normal`、`--rf-status-watch`、`--rf-status-warning`、`--rf-status-critical`、`--rf-status-empty` 及对应背景、描边变量，并在 Tailwind 配置中暴露 `status.*` 和补充 `rice.dark`、`rice.deep` 语义色。
- 新增 shadcn-vue 源码组件 `alert` 与 `toggle-group`，保留为 `src/components/ui` 原子组件；`toggle-group` 依赖同目录 `toggle` 源码组件，未批量新增后续页面暂不需要的组件。
- 将 `StatusTag` 与 `MetricValueTag` 调整为统一读取 `src/utils/status.ts` 的状态 token 映射，前端展示固定收敛为正常、关注、预警、严重、无数据。
- 新增 `src/components/base/AppShell.vue` 并让 `MainLayout` 切换到 `base` 组件边界；迁移期暂不删除 `src/components/workbench`，不改写 `/overview` 与 `/map-twin` 页面结构。
- 将 `AppHeader`、`AppSidebar`、`PageContainer`、`StatCard`、`ChartCard`、`StatusTag`、`MetricValueTag`、`FilterBar`、`EmptyState`、`LoadingState` 等基础组件迁移为 Tailwind CSS + shadcn-vue 风格实现。
- 将 `MetricSelector`、`DateSelector`、`RegionSelector` 改为不依赖 Ant Design Vue 的基础筛选控件，并新增 `SelectControl`、`DateRangeSelector` 供筛选区复用。
- 将 `DataTable` 从 Ant Design Vue `a-table` 迁移为基于 shadcn-vue table 源码组件和项目自定义分页/横向滚动的实现，保留 `columns`、`dataSource`、`rowKey`、`rowClassName`、`pagination`、`scroll` 和 `bodyCell` slot 兼容。
- 新增 `src/types/table.ts` 项目表格类型，页面表格列定义不再从 `ant-design-vue` 导入 `TableColumnsType`。
- 移除全局样式中针对 Ant Design Vue table 的覆盖，保留按钮、选择器、日期等迁移期仍被业务页面使用的 `.ant-*` 兼容样式。

### 文档更新

- 统一前端 UI 迁移方向：目标前端栈调整为 Vue 3 + TypeScript + Vite + Tailwind CSS + shadcn-vue + Reka UI + ECharts + CesiumJS + Axios，并明确 Vue Router 与 Pinia 继续保留。
- 明确 Ant Design Vue 为待移除旧依赖，在运行时代码仍有引用前不删除依赖、全局注册、主题配置和 `vendor-antd` 分包。
- 更新组件迁移策略：`src/components/ui` 存放 shadcn-vue 源码组件，`src/components/base` 存放项目语义组件，页面优先使用 `base` 组件，不直接散落大量 `ui` 原子组件。
- 明确本轮迁移不修改后端 API、数据模型、模拟数据生成逻辑，不恢复 Excel、GeoJSON、PDF、图片导入，不扩大 `/overview`、`/map-twin`、`/plot-detail/:plotId?`、`/metric-compare`、`/warnings`、`/system-docs` 六页闭环。
- 更新设计系统和前端指南，补充基础组件迁移完成状态、`DataTable` 兼容策略、`FilterBar` 不依赖 AntD DOM 样式的规则，以及下一轮业务页面 AntD 标签迁移方向。
- 更新设计系统和前端指南，明确 `base/AppShell` 是当前主布局边界，`workbench` 为迁移期遗留目录；明确 `src/components/ui` 当前补齐 `alert`、`toggle-group`，状态展示统一通过 `--rf-status-*` token 与 `src/utils/status.ts` 映射。

### 验证

- 已执行：`git status --short --branch`。
- 已执行：`rg "ant-design-vue|<a-|</a-|\\.ant-|ConfigProvider|themeConfig|vendor-antd" frontend`，确认 AntD 仍有运行时代码引用，本轮未删除依赖。
- 已执行文档与前端冲突标记扫描，未发现 merge conflict 标记。
- 已通过：`npm --prefix frontend run test:overview`。
- 已通过：`npm --prefix frontend run test:page-linkage`。
- 已通过：`npm --prefix frontend run test:twin-analysis`。
- 已通过：`npm --prefix frontend run test:map`。
- 已通过：`npm --prefix frontend run build`（仍存在既有 Cesium/Ant Design Vue 大 chunk 警告）。

## 2026-06-08

### 新增

- 新增 `.codex/skills/ricefield-insight-platform/SKILL.md` 项目专用 Codex skill，固化稻田智研平台 MVP 边界、数据治理、文档同步、验证和提交要求。
- 新增 `.codex/skills/ricefield-insight-platform/agents/openai.yaml`，为项目专用 skill 提供 Codex UI 元数据。
- 新增 `docs/superpowers/specs/2026-06-08-tailwind-shadcn-vue-frontend-redesign-design.md`，沉淀前端整体重构设计。
- 新增 `docs/superpowers/plans/2026-06-08-tailwind-shadcn-vue-frontend-redesign.md`，拆解 Tailwind CSS + shadcn-vue 前端迁移实施计划。
- 新增 Tailwind 工作台外壳组件 `AppShell`、`AppSidebar`、`CommandBar` 和统一导出入口，为后续六页逐步迁移提供基础布局。
- 新增工作台数据组件 `StatusBadge`、`MetricValue`、`DataPanel`，统一状态标签、指标数值和分析面板的非 AntD 表达方式。
- 新增工作台包装组件 `InspectorPanel` 和 `TwinMapPanel`，用于承载地图主画布与右侧对象详情。

### 修改

- 明确下一轮前端优化方向调整为 Tailwind CSS + shadcn-vue 源码组件体系，计划完全移除 Ant Design Vue。
- 明确六页统一重构路线：先统一 App Shell 和组件系统，再逐页重构场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析和系统说明。
- 将主布局切换到新的 Tailwind 工作台外壳，保留 Ant Design Vue 全局注册，确保未迁移页面在分阶段迁移期间继续可用。
- 将场景驾驶舱和 Cesium 地图孪生页迁移到新的 CommandBar、地图主画布、右侧 Inspector 和工作台数据组件结构。
- 移除场景驾驶舱和 Cesium 地图孪生页内的直接 Ant Design Vue 标签、AntD 表格和 AntD 类型依赖，保留 Cesium 地图内核与现有数据服务契约。
- 补充地图分析服务 `findFeatureByPlotId` 工具函数，支持迁移后的地图页根据路由或选中地块恢复 Feature 状态。

### 验证

- 已通过：`backend\.venv\Scripts\python.exe C:\Users\Monso\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\.codex\skills\ricefield-insight-platform`。
- 本次仅更新项目专用 Codex skill、`.gitignore`、设计规格、实施计划和变更记录，未修改业务代码，未运行前后端测试。
- 已通过：`npm --prefix frontend run build`。
- 已通过：`npm --prefix frontend run test:overview`。
- 已通过：`npm --prefix frontend run test:map`。
- 已通过 Playwright CLI 基本打开验证：`/overview` 与 `/map-twin?plotId=demo-ricefield-2025-A01` 可访问；仅存在既有 `favicon.ico` 404。
- 构建仍存在 Cesium 和 Ant Design Vue 相关大 chunk 警告，属于既有体积问题，后续页面迁移和 AntD 移除阶段再处理。

## 2026-05-27

### 新增

- 新增 `docs/DEMO_SCRIPT.md`，补充 3 分钟演示脚本，按演示目标、准备工作、页面顺序、讲解词、点击动作、预期画面和注意事项组织。
- 新增 `docs/RELEASE_CHECKLIST.md`，整理第一阶段发布范围、已完成能力、不做事项、演示路径、验证命令、数据合规检查、已知风险和进入第二阶段前置条件。

### 修改

- 优化 `场景驾驶舱` 首页信息层级：将孪生健康度、待核查预警数量、最近观测日期和地图/预警入口整合到横幅右侧判断区，避免健康度与普通 KPI 平铺竞争。
- 将首页横幅下方 KPI 收敛为地块数量、指标数量、预警数量和观测天数 4 个支撑指标，降低首屏噪声，让用户先判断状态再进入地图或预警分析。
- 优化关键指标概览卡片的内边距、状态色边和辅助说明，提升作物长势、叶绿素、氮、pH、叶面积指数的可读性。
- 统一基础排版细节，补充全局字体、字号和行高基线，移除 `StatCard` 数字负字距，改善卡片文字与边框距离。
- 梳理当前 git 分支和最近提交记录，确认实际开发仍在 `claude/digital-twin-dev` 上推进，且本地分支相对远端已有连续文档与六页回归提交。
- 修正 `README.md`、`docs/CLAUDE_WORKFLOW.md`、`docs/CODEX_WORKFLOW.md` 和 `AGENTS.md` 中“Claude 优先 / Codex 暂停使用”的过时表述，改为 Claude 与 Codex 都可基于当前活跃分支继续协作。
- 明确当前分支使用方式：默认继续使用当前活跃分支，不因工具名称另起分支；切换基准分支、push、创建 PR、回退历史或强制推送前必须先确认。
- 修复 `指标对比` 页面未注册 Ant Design Vue `Alert` 组件导致的控制台警告。
- 优化 `Cesium 地图孪生` 移动端地图浮层布局，压缩筛选条并下移地图工具按钮，避免工具按钮遮挡查询、重置和区域筛选控件。

### 文档更新

- 更新 `README.md` 开发协作说明，将 Claude/Codex 文档入口改为协作注意事项，并补充分支、提交、文档同步和确认要求。
- 重写 `docs/CLAUDE_WORKFLOW.md`，保留 Claude 参与时的检查清单、禁止事项、验证命令、文档同步、提交和最终回复要求。
- 重写 `docs/CODEX_WORKFLOW.md`，明确 Codex 当前可用，并补充分支检查、开发顺序、确认点、验证命令、文档同步和提交要求。
- 更新 `AGENTS.md`，新增当前协作流程，明确当前主线分支、提交要求、禁止未经授权 push/PR/改写历史，以及流程类文档同步范围。
- 更新 `README.md` 文档入口，加入 `docs/DEMO_SCRIPT.md`。
- 更新 `README.md` 文档入口，加入 `docs/RELEASE_CHECKLIST.md`。
- 演示脚本明确第一阶段只使用后端程序生成的模拟数据，不展示真实客户数据，不引入 Excel、GeoJSON、PDF、图片导入主线。
- 发布检查清单明确第一阶段只发布模拟数据驱动的六页 MVP，不把 Excel、GeoJSON、PDF、图片导入、真实客户数据、报告导出或二期能力纳入发布主线。
- 更新 `docs/DESIGN_SYSTEM.md`，补充场景驾驶舱首屏判断区和首页 4 个支撑 KPI 的布局规范。
- 更新 `docs/DESIGN_SYSTEM.md`，补充移动端地图筛选浮层与地图工具按钮不得互相遮挡的规范。

### 验证

- 已通过首页视觉验证：使用 Playwright 截图检查 `/overview` 桌面 1440x1000 与移动 390x844 视口，确认健康度判断区、KPI 行和关键指标卡正常渲染，无文字溢出。
- 已通过前端构建：`npm --prefix frontend run build`（构建成功；保留既有 Cesium/Ant Design 大 chunk 提示）。
- 本次首页视觉优化未修改后端代码、依赖、API 契约、数据字段或运行时配置。
- 已通过本地检查：`git status --short --branch`、`git log --oneline -n 8`，确认当前分支和最近提交记录。
- 已通过第一阶段发布检查清单验证：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp_codex_release`（19 passed）。
- 已通过第一阶段发布检查清单前端服务测试：`npm --prefix frontend run test:overview`、`npm --prefix frontend run test:page-linkage`、`npm --prefix frontend run test:twin-analysis`、`npm --prefix frontend run test:map`。
- 已通过第一阶段发布检查清单前端构建：`npm --prefix frontend run build`（构建成功；保留既有 Cesium/Ant Design 大 chunk 提示）。
- 已执行六页浏览器回归，覆盖 `/overview`、`/map-twin`、`/plot-detail/demo-ricefield-2025-A04`、`/metric-compare`、`/warnings`、`/system-docs` 的桌面 1440x980 与移动 390x844 视口。
- 已验证上述页面无白屏、无框架错误覆盖层、无关键控制台错误；地图 canvas 与 ECharts 图表均正常渲染；地块画像“定位到地图”、指标对比“查看画像”和预警分析“查看画像”跳转正常。
- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q --basetemp=backend\.pytest_tmp_codex_regression`（19 passed）。首次直接运行受系统临时目录 `C:\Users\Monso\AppData\Local\Temp\pytest-of-Monso` 权限影响失败，改用仓库内临时目录后通过。
- 已通过前端服务测试：`npm --prefix frontend run test:overview`、`npm --prefix frontend run test:page-linkage`、`npm --prefix frontend run test:twin-analysis`、`npm --prefix frontend run test:map`。
- 已通过前端构建：`npm --prefix frontend run build`（构建成功；保留既有 Cesium/Ant Design 大 chunk 提示）。

## 2026-05-26

### 新增

- 新增 `docs/NEXT_ACTION_TODO.md`，将下一步工作拆分为演示脚本、六页回归、地图稳定性、地块画像、指标对比、预警语义、API 类型契约、本地临时目录、部署说明和第一阶段发布检查 10 个可执行待办。
- 每个待办补充目标、建议修改范围、验收命令和可直接复制给 Codex 的提示词，便于后续按任务顺序推进。

### 修改

- 按 `docs/design-reference/system-docs-reference.png` 优化 `系统说明` 页面为项目说明中心，覆盖平台定位、当前数据说明、数字孪生构建流程、当前系统功能、数据来源与生成方式、系统边界、未来演进方向、文档索引和页脚。
- 更新 `README.md` 文档入口，加入下一步待办执行计划。
- 当前数据说明改为优先读取后端标准化 API，展示数据模式、场景 ID、地块数量、指标数量、时间范围和预警数量；页面明确当前为程序生成的模拟数据，不展示真实采集数据或客户来源数据。
- 文档索引由旧表格目录改为文档卡片网格，包含项目计划、系统架构、数据模型、API、设计系统、前端指南、后端指南、用户手册、部署说明、模拟数据指南、指标字典和变更记录；入口仅展示本地仓库路径，不伪装在线文档跳转。
- 更新系统说明页响应式布局，桌面端数字孪生构建流程保持 6 步横向流程卡展示，窄屏纵向堆叠。
- 同步更新系统说明页路由副标题为“了解平台定位、数据来源、功能边界与未来规划。”。

### 文档更新

- 更新 `docs/DESIGN_SYSTEM.md`，补充系统说明页作为说明型页面的布局规范、流程卡片、边界说明卡、未来演进卡和文档索引卡规范。
- 更新 `docs/USER_MANUAL.md`，补充系统说明页展示内容、数据说明、边界说明和文档入口使用方式。
- 更新 `docs/PROJECT_PLAN.md`，将项目定位表述收敛为面向科研展示、项目汇报与教学演示。
- 更新 `README.md`，补充 `docs/NEXT_ACTION_TODO.md` 文档入口。

### 验证

- 本次新增待办文档和 README 入口，不涉及后端代码、前端代码、API 契约或运行时配置，未运行完整前后端测试。
- 已通过后端测试：`backend\.venv\Scripts\python.exe -m pytest backend\tests -q`（首次受系统临时目录权限影响失败，改用仓库内临时目录后 19 passed）。
- 已通过前端服务测试：`npm --prefix frontend run test:overview`、`npm --prefix frontend run test:page-linkage`、`npm --prefix frontend run test:twin-analysis`、`npm --prefix frontend run test:map`。
- 已通过前端构建：`npm --prefix frontend run build`（构建成功；保留既有 Cesium/Ant Design 大 chunk 提示）。
- 已通过 Playwright 截图验证：`/system-docs` 桌面 1440x980 与移动 390x844 视口渲染正常；桌面流程卡保持 6 步横向展示，移动端按单列堆叠。

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
