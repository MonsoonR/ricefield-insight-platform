# 稻田智研平台

稻田智研平台（RiceField Insight Platform）是面向大创答辩与科研展示的稻田数字孪生可视化平台。新版第一阶段聚焦一个可直接演示的数字孪生闭环：场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析和系统说明。

项目不接入、不保存、不展示真实客户数据文件。默认演示数据由后端程序生成，包括示例稻田场景、8 个地块边界、11 个指标、45 天时序观测和 6 条预警事件。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vue 3、TypeScript、Vite、Vue Router、Pinia、Ant Design Vue、ECharts、CesiumJS、Axios |
| 后端 | FastAPI、Pydantic、SQLAlchemy、Alembic、Pytest |
| 默认数据层 | 程序生成模拟场景 |
| 可选正式层 | PostgreSQL + PostGIS |
| 部署 | Nginx、Docker Compose |

第一阶段已移除 Excel、GeoJSON 文件导入、导入中心和导入质量报告主线。

## 页面闭环

- 场景驾驶舱：展示当前数字孪生场景、健康度、观测天数、预警数量和区域状态。
- Cesium 地图孪生：在卫星底图上展示地块边界、指标着色、点击详情和趋势联动。
- 地块画像：查看单个地块基础信息、多指标快照、趋势和数据来源。
- 指标对比：按指标、日期和区域对比各地块状态。
- 预警分析：展示缺失、异常和错误预警，并在地图上定位地块。
- 系统说明：集中展示项目文档索引。

## 本地启动

```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
npm --prefix frontend run dev
```

默认不需要数据库或本地数据文件。

如需使用 PostGIS 可选正式层：

```powershell
$env:APP_DATA_BACKEND="postgres"
$env:DATABASE_URL="postgresql+psycopg://ricefield:ricefield@127.0.0.1:5432/ricefield"
backend\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

## 文档入口

| 文档 | 用途 |
|---|---|
| `docs/PROJECT_PLAN.md` | 项目定位、MVP 范围和阶段目标 |
| `docs/ARCHITECTURE.md` | 前后端、数据层和地图可视化架构 |
| `docs/DATA_MODEL.md` | 数字孪生场景、地块、指标、观测和预警模型 |
| `docs/METRIC_DICTIONARY.md` | 第一阶段演示指标字典 |
| `docs/API.md` | 后端 API 契约 |
| `docs/DESIGN_SYSTEM.md` | 界面布局、视觉和交互规范 |
| `docs/IMPORT_GUIDE.md` | 模拟场景与数据生成指南 |
| `docs/USER_MANUAL.md` | 页面使用说明 |
| `docs/DEMO_SCRIPT.md` | 3 分钟演示脚本 |
| `docs/RELEASE_CHECKLIST.md` | 第一阶段发布检查清单 |
| `docs/NEXT_ACTION_TODO.md` | 下一步待办执行计划与 Codex 提示词 |
| `docs/CLAUDE_WORKFLOW.md` | Claude 协作注意事项 |
| `docs/CODEX_WORKFLOW.md` | Codex 协作注意事项 |
| `docs/CHANGELOG.md` | 变更记录 |

## 开发协作

当前协作以 `AGENTS.md`、当前活跃分支和任务上下文为准，不再使用“Claude 优先 / Codex 暂停”的旧流程。Claude 和 Codex 都可以继续参与开发，但必须先检查 `git status --short --branch`、最近提交和未提交改动，避免覆盖用户或其他工具的工作。

截至本次梳理，当前主线开发分支为 `claude/digital-twin-dev`，它承接 `codex/digital-twin-clean` 之后的数字孪生主线。后续如果没有用户明确要求新建分支，继续在当前活跃分支上完成任务；如需切换基准分支、回合并 `main`、推送远端或创建 PR，先向用户确认。

每次实际更新都必须同步 `docs/CHANGELOG.md`，涉及数据字段、指标编码、API、页面结构、设计规范、模拟数据规则或部署方式时，同时更新对应专题文档。完成验证后创建 Git commit；纯文档改动可以跳过前后端完整测试，但最终说明必须写明原因。Claude 细节见 [`docs/CLAUDE_WORKFLOW.md`](docs/CLAUDE_WORKFLOW.md)，Codex 细节见 [`docs/CODEX_WORKFLOW.md`](docs/CODEX_WORKFLOW.md)。

