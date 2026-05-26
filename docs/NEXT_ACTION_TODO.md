# 下一步待办执行计划

## 使用方式

本文档用于把接下来的工作拆成可独立执行的任务。每个任务都包含目标、建议修改范围、验收方式和可直接复制给 Codex 的提示词。

执行原则：

- 严格保持第一阶段 MVP 边界：程序生成模拟数据、六页演示闭环、标准化 API。
- 不新增 Excel、GeoJSON、PDF、图片导入，不接入真实客户数据。
- 不提前实现权限系统、自动报告、多项目管理、复杂三维资产或复杂空间分析。
- 每次改动都同步更新相关文档和 `docs/CHANGELOG.md`。
- 每个任务完成后先验证，再提交 Git。

## 待办目录

| 顺序 | 任务 | 目标 | 预计产出 |
|---|---|---|---|
| 1 | 演示脚本收口 | 固化 3 分钟演示路径 | `docs/DEMO_SCRIPT.md` 或更新 `docs/USER_MANUAL.md` |
| 2 | 六页浏览器回归 | 确认可演示页面无明显交互和布局问题 | 页面问题清单或修复提交 |
| 3 | 地图页演示稳定性优化 | 确保 `/map-twin` 首屏、点击、定位稳定 | 地图页小修和验证记录 |
| 4 | 地块画像信息核对 | 确保模拟字段、指标快照、趋势、批次表达一致 | 画像页小修和文档同步 |
| 5 | 指标对比页口径固化 | 固化排名、均值、状态、较昨日变化的计算口径 | 服务测试和页面说明 |
| 6 | 预警分析页语义核对 | 确保预警类型、严重程度、建议文案谨慎可信 | 预警文案和映射规则同步 |
| 7 | API 与前端类型契约核查 | 防止接口文档、Pydantic schema、前端类型漂移 | 契约修正和测试 |
| 8 | 本地临时目录与忽略规则整理 | 清理权限警告和非仓库产物干扰 | 清理说明或 `.gitignore` 微调 |
| 9 | 部署与启动说明校验 | 让评审或维护人员能按文档启动 | `README.md` / `docs/DEPLOYMENT.md` 更新 |
| 10 | 第一阶段发布检查 | 汇总验证命令、演示路径、剩余风险 | 发布检查清单和最终提交 |

## 1. 演示脚本收口

目标：把当前“六页闭环”整理成一条稳定的 3 分钟演示路径，明确讲什么、点哪里、预期看到什么。

建议范围：

- 新增 `docs/DEMO_SCRIPT.md`，或在 `docs/USER_MANUAL.md` 增加“演示流程”章节。
- 覆盖页面顺序：场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析、系统说明。
- 明确当前数据是程序生成模拟数据，不能暗示真实采集或客户来源。

验收方式：

```powershell
git diff -- docs
```

Codex 提示词：

```text
请在当前仓库中为稻田智研平台补充一份 3 分钟演示脚本文档。先阅读 README.md、docs/PROJECT_PLAN.md、docs/USER_MANUAL.md、docs/API.md 和 docs/CHANGELOG.md，确认当前第一阶段边界。然后新增 docs/DEMO_SCRIPT.md，按“演示目标、准备工作、页面顺序、讲解词、点击动作、预期画面、注意事项”组织。必须强调当前只使用后端程序生成的模拟数据，不展示真实客户数据，不引入 Excel/GeoJSON/PDF/图片导入主线。同步更新 README.md 的文档入口和 docs/CHANGELOG.md。完成后运行必要的文档检查和 git diff，不要修改无关代码。
```

## 2. 六页浏览器回归

目标：实际打开六个页面，检查桌面和移动视口下是否有白屏、遮挡、溢出、跳转失败、控制台错误。

建议范围：

- 启动后端和前端开发服务。
- 检查 `/overview`、`/map-twin`、`/plot-detail/demo-ricefield-2025-A04`、`/metric-compare`、`/warnings`、`/system-docs`。
- 优先记录问题，不先扩大功能。

验收方式：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
npm --prefix frontend run build
```

Codex 提示词：

```text
请对稻田智研平台做一次六页浏览器回归。先启动后端和前端服务，然后用浏览器检查 /overview、/map-twin、/plot-detail/demo-ricefield-2025-A04、/metric-compare、/warnings、/system-docs 的桌面和移动视口。重点看白屏、控制台错误、文字遮挡、表格溢出、地图空白、图表不渲染、地块画像和地图定位跳转失败。只修复第一阶段 MVP 内的问题，不新增二期能力，不引入真实数据或文件导入。完成后运行后端测试、前端四组服务测试和前端构建，并同步更新 docs/CHANGELOG.md。
```

## 3. 地图页演示稳定性优化

目标：让 `Cesium 地图孪生` 成为演示中最稳定的核心页，重点保证首屏地图、地块点击、指标着色、趋势联动、画像跳转。

建议范围：

- `frontend/src/pages/MapAnalysisPage.vue`
- `frontend/src/components/base/CesiumMapPanel.vue`
- `frontend/src/services/mapAnalysis.ts`
- `docs/FRONTEND_GUIDE.md`
- `docs/DESIGN_SYSTEM.md`

验收方式：

```powershell
npm --prefix frontend run test:map
npm --prefix frontend run build
```

Codex 提示词：

```text
请聚焦优化 Cesium 地图孪生页的演示稳定性。先阅读 frontend/src/pages/MapAnalysisPage.vue、frontend/src/components/base/CesiumMapPanel.vue、frontend/src/services/mapAnalysis.ts、docs/FRONTEND_GUIDE.md 和 docs/DESIGN_SYSTEM.md。检查并修复地图首屏高度、地块编号可见性、选中态、图层开关、/map-twin?plotId=xxx 定位、查看画像跳转和趋势联动中的明显问题。不得新增测距、绘制、编辑、GeoJSON 导入、上传或复杂 GIS 功能。完成后运行 npm --prefix frontend run test:map 和 npm --prefix frontend run build，并更新 docs/CHANGELOG.md；如改了交互规则，同步更新前端指南或设计系统。
```

## 4. 地块画像信息核对

目标：确保单地块画像里的模拟字段、指标快照、趋势、批次、预警建议都可信且不误导。

建议范围：

- `frontend/src/pages/PlotDetailPage.vue`
- `frontend/src/services/twinAnalysis.ts`
- `frontend/src/types/api.ts`
- `docs/USER_MANUAL.md`
- `docs/DESIGN_SYSTEM.md`

验收方式：

```powershell
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:page-linkage
npm --prefix frontend run build
```

Codex 提示词：

```text
请核对并完善地块画像页的信息表达。先阅读 frontend/src/pages/PlotDetailPage.vue、frontend/src/services/twinAnalysis.ts、docs/DESIGN_SYSTEM.md 和 docs/USER_MANUAL.md。重点检查：模拟字段是否明确标注，11 个指标快照是否与指标字典一致，趋势时间范围是否适配 2025-06-01 到 2025-07-15 的演示数据，观测批次是否保留 batch_id 和 data_source_id，预警建议是否谨慎且不编造农艺处方。只修正第一阶段页面和文档，不新增后端字段，除非发现契约缺陷并同步 API/schema/测试。完成后运行 twin-analysis、page-linkage 测试和前端构建，并更新 docs/CHANGELOG.md。
```

## 5. 指标对比页口径固化

目标：把指标对比页的排名、均值、最高值、最低值、异常地块数、较昨日变化等计算口径固定下来，避免演示时解释不清。

建议范围：

- `frontend/src/pages/MetricComparePage.vue`
- `frontend/src/services/twinAnalysis.ts`
- `frontend/src/services/__tests__/twinAnalysis.test.mjs`
- `docs/FRONTEND_GUIDE.md`
- `docs/USER_MANUAL.md`

验收方式：

```powershell
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run build
```

Codex 提示词：

```text
请固化指标对比页的计算和展示口径。先阅读 frontend/src/pages/MetricComparePage.vue、frontend/src/services/twinAnalysis.ts、frontend/src/services/__tests__/twinAnalysis.test.mjs、docs/FRONTEND_GUIDE.md 和 docs/USER_MANUAL.md。确认排名、均值、最高值、最低值、异常地块数、较均值差值、较昨日变化、区域对比和状态分布的来源与算法。优先补测试和说明，只有发现实际错误才改代码。不得新增后端 API 字段，不引入复杂统计分析。完成后运行 npm --prefix frontend run test:twin-analysis 和 npm --prefix frontend run build，并更新 docs/CHANGELOG.md。
```

## 6. 预警分析页语义核对

目标：确保预警分析页从技术枚举到中文业务语义的映射清晰、谨慎、可解释。

建议范围：

- `frontend/src/pages/WarningAnalysisPage.vue`
- `frontend/src/services/twinAnalysis.ts`
- `backend/app/services/demo_data.py`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/USER_MANUAL.md`

验收方式：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run build
```

Codex 提示词：

```text
请核对预警分析页的语义映射和建议文案。先阅读 frontend/src/pages/WarningAnalysisPage.vue、frontend/src/services/twinAnalysis.ts、backend/app/services/demo_data.py、docs/API.md、docs/DATA_MODEL.md 和 docs/USER_MANUAL.md。检查 missing/outlier/error 到中文预警类型、严重等级、地图颜色、最新预警列表和明细表的映射是否一致。建议文案必须谨慎，不直接给具体农艺处方，不伪装真实监测结论。若只改前端语义，避免新增后端字段；若后端预警结构确实需要变更，必须同步 schema、API 文档、数据模型和测试。完成后运行后端测试、twin-analysis 测试和前端构建，并更新 docs/CHANGELOG.md。
```

## 7. API 与前端类型契约核查

目标：系统性检查 Pydantic schema、API 文档、前端 TypeScript 类型是否一致，减少后续迭代踩坑。

建议范围：

- `backend/app/schemas/mvp_api.py`
- `backend/app/schemas/data_model.py`
- `frontend/src/types/api.ts`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `backend/tests/test_mvp_api.py`

验收方式：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
npm --prefix frontend run build
```

Codex 提示词：

```text
请做一次 API 与前端类型契约核查。先阅读 backend/app/schemas/mvp_api.py、backend/app/schemas/data_model.py、frontend/src/types/api.ts、docs/API.md、docs/DATA_MODEL.md 和 backend/tests/test_mvp_api.py。逐项核对场景、指标、地块、日期、地图图层、地块摘要、趋势、指标对比、预警分析的字段命名、可空性、状态枚举和日期字段。修复明显不一致处，优先保持现有 API 稳定；任何字段新增或删除都必须同步后端测试、前端类型和文档。完成后运行后端测试和前端构建，并更新 docs/CHANGELOG.md。
```

## 8. 本地临时目录与忽略规则整理

目标：减少 `git status --ignored` 和测试临时目录权限警告对协作的干扰。

建议范围：

- `.gitignore`
- `backend/pytest.ini`
- 本地未跟踪临时目录
- `docs/CLAUDE_WORKFLOW.md`
- `docs/CODEX_WORKFLOW.md`

验收方式：

```powershell
git status --short --ignored
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
```

Codex 提示词：

```text
请整理本地临时目录和忽略规则，目标是减少 pytest 临时目录权限警告和无关产物干扰。先查看 git status --short --ignored、.gitignore、backend/pytest.ini、docs/CLAUDE_WORKFLOW.md 和 docs/CODEX_WORKFLOW.md。只能清理未跟踪的缓存、构建产物、临时测试目录和本地依赖，不得删除任何已跟踪源码、文档、设计参考图或用户数据。必要时微调 .gitignore 或测试临时目录说明。完成后运行 git status、后端测试，并更新 docs/CHANGELOG.md。执行任何递归删除前必须确认目标路径在当前仓库的临时/缓存目录内。
```

## 9. 部署与启动说明校验

目标：让维护人员按文档能启动默认演示，不依赖数据库或真实数据文件。

建议范围：

- `README.md`
- `docs/DEPLOYMENT.md`
- `.env.example`
- `frontend/.env.example`
- `backend/alembic.ini`

验收方式：

```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
npm --prefix frontend run dev
npm --prefix frontend run build
```

Codex 提示词：

```text
请校验并完善稻田智研平台的本地启动和部署说明。先阅读 README.md、docs/DEPLOYMENT.md、.env.example、frontend/.env.example 和 backend/alembic.ini。确认默认演示模式不需要数据库或本地数据文件，PostGIS 只作为可选正式层说明。修正文档中不准确、过时或容易误导的启动步骤，不引入新部署技术，不添加真实数据路径。完成后运行前端构建；如改到后端启动配置，运行后端测试。同步更新 docs/CHANGELOG.md。
```

## 10. 第一阶段发布检查

目标：在进入第二阶段前，形成一份清晰的发布检查记录，说明已完成能力、验证命令、剩余风险和不做事项。

建议范围：

- 新增 `docs/RELEASE_CHECKLIST.md`
- `docs/PROJECT_PLAN.md`
- `docs/CHANGELOG.md`
- `README.md`

验收方式：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
npm --prefix frontend run build
git status --short
```

Codex 提示词：

```text
请为稻田智研平台整理第一阶段发布检查清单。先阅读 README.md、docs/PROJECT_PLAN.md、docs/API.md、docs/DATA_MODEL.md、docs/USER_MANUAL.md、docs/CHANGELOG.md 和当前测试脚本。新增 docs/RELEASE_CHECKLIST.md，按“发布范围、已完成能力、不做事项、演示路径、验证命令、数据合规检查、已知风险、进入第二阶段前置条件”组织。不要新增功能代码。完成后运行后端测试、前端四组服务测试和前端构建，更新 docs/CHANGELOG.md，并提交 Git。
```

## 推荐执行节奏

第一轮只做任务 1、2、10，目标是把当前系统收口成可演示版本。  
第二轮做任务 3、4、5、6，目标是针对演示中暴露的问题做小范围修复。  
第三轮做任务 7、8、9，目标是提高后续协作和维护稳定性。

如果时间有限，最短路径是：

1. 完成演示脚本。
2. 做六页浏览器回归。
3. 修复阻碍演示的问题。
4. 写发布检查清单。
5. 跑完整验证并提交。
