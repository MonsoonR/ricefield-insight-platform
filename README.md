# 稻田智研平台

稻田智研平台（RiceField Insight Platform）是面向研究所研究人员的农田数据可视化与分析平台，重点服务水稻试验田、农田地块和环境指标研究。

第一版目标是把定期提供的 Excel 数据和地块 GeoJSON 数据统一整理为可复用的数据结构，并通过地图、图表、表格和质量报告帮助研究人员查看地块状态、指标趋势和数据问题。

## 技术栈

本仓库遵循 `docs/PROJECT_PLAN.md` 中已经讨论过的技术方案，本次初始化不引入新技术，也不实现业务代码。

| 层级 | 技术 |
|---|---|
| 前端 | Vue 3、TypeScript、Vite、Vue Router、Pinia、Ant Design Vue、ECharts、CesiumJS、Axios |
| 后端 | FastAPI、Pydantic、pandas、openpyxl、SQLAlchemy、Alembic、Pytest |
| 数据 | MVP 阶段优先使用标准化 JSON / CSV / 可选 SQLite，正式阶段再接入 PostgreSQL + PostGIS |
| 部署 | Nginx、Docker Compose |
| 协作 | GitHub、GitHub Actions |

## 目录结构

```text
ricefield-insight-platform/
├── backend/              后端服务目录，后续放置 FastAPI 应用、数据解析、服务层和测试
├── frontend/             前端应用目录，后续放置 Vue 3 页面、组件、路由、状态和样式
├── data/                 本地数据目录，存放原始数据、标准化结果和质量报告；不提交真实数据
├── docs/                 项目规划、架构、接口、数据模型、设计规范和使用文档
├── deploy/               部署配置目录，后续放置 Docker Compose、Nginx 和内网部署说明
├── scripts/              工程脚本目录，后续放置数据处理、检查、导入等辅助脚本
├── tests/                跨模块或端到端测试目录；后端单元测试可按后续工程结构放置
└── .github/workflows/    GitHub Actions 工作流目录
```

## 本地开发方式

当前阶段仅完成仓库初始化，尚未生成前端和后端工程文件，因此没有可启动的本地服务。

后续初始化工程后，建议按以下顺序开发：

1. 阅读 `docs/PROJECT_PLAN.md`，确认当前阶段目标。
2. 阅读 `docs/DATA_MODEL.md` 和 `docs/METRIC_DICTIONARY.md`，先固定数据结构和指标字典。
3. 初始化后端 FastAPI 工程，优先完成 Excel / GeoJSON 解析和质量报告。
4. 初始化前端 Vue 3 工程，优先搭建统一布局和设计规范。
5. 再接入地图、图表和导入中心等业务页面。

## 文档入口

| 文档 | 用途 |
|---|---|
| `docs/PROJECT_PLAN.md` | 项目总体规划和阶段目标 |
| `docs/ARCHITECTURE.md` | 系统架构与模块边界 |
| `docs/DATA_MODEL.md` | 核心数据模型和字段约定 |
| `docs/METRIC_DICTIONARY.md` | 指标字典和指标治理规则 |
| `docs/API.md` | API 草案与接口设计原则 |
| `docs/DESIGN_SYSTEM.md` | 中文优先的数据分析界面设计规范 |
| `docs/FRONTEND_GUIDE.md` | 前端开发约定 |
| `docs/BACKEND_GUIDE.md` | 后端开发约定 |
| `docs/IMPORT_GUIDE.md` | 数据导入与质量报告说明 |
| `docs/USER_MANUAL.md` | 用户使用手册入口 |
| `docs/DEPLOYMENT.md` | 部署与运维说明 |
| `docs/CHANGELOG.md` | 版本变更记录 |
