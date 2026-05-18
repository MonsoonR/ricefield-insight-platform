# Codex 协作流程

## 当前阶段说明（重要）

当前阶段全程优先使用 Claude 进行开发，Codex 暂停使用。日常开发请遵循 [`docs/CLAUDE_WORKFLOW.md`](./CLAUDE_WORKFLOW.md)。本文件保留为后续 Codex 重新介入时的参考基准，不作为当前主流程。

当前开发目标已调整为"先做好系统功能和工程结构"，不再以"大创答辩 PPT"作为核心开发任务。大创答辩保留为后续展示场景。

## 当前项目基准

项目是面向科研展示的"稻田数字孪生可视化平台"。后续任务必须围绕以下主线推进：

- 场景驾驶舱；
- Cesium 地图孪生；
- 地块画像；
- 指标对比；
- 预警分析；
- 系统说明。

第一阶段不实现 Excel、GeoJSON、PDF、图片等文件导入，不恢复数据导入中心，不新增导入报告接口。

## 开发前检查

1. 阅读 `AGENTS.md` 和相关 docs。
2. 检查 `git status --short`，不要覆盖用户未提交改动。
3. 若修改数据字段、指标、API、页面结构或部署方式，同步更新文档。
4. 行为变更先写测试。

## 推荐任务顺序

1. 数据模型和 schema。
2. 后端 service。
3. 后端 API。
4. 前端 API 类型。
5. 前端页面和组件。
6. 文档与 changelog。
7. 测试、构建和浏览器验证。

## 验证命令

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
npm --prefix frontend run build
```

## 文档同步

优先更新：

- `docs/PROJECT_PLAN.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/DESIGN_SYSTEM.md`
- `docs/FRONTEND_GUIDE.md`
- `docs/BACKEND_GUIDE.md`
- `docs/IMPORT_GUIDE.md`
- `docs/METRIC_DICTIONARY.md`
- `docs/USER_MANUAL.md`
- `docs/DEPLOYMENT.md`
- `docs/CHANGELOG.md`

`docs/IMPORT_GUIDE.md` 保留文件名，但内容是模拟场景与数据生成指南。

## 提交要求

每次完成实际更新并通过验证后提交 Git。提交前确认暂存范围，不提交虚拟环境、缓存、真实数据文件、构建产物或无关文件。
