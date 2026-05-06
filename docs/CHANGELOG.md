# 变更记录

## 2026-05-06

- 初始化项目仓库目录结构。
- 创建中文优先的 README 和基础文档入口。
- 创建 `.gitignore`，排除依赖、缓存、构建产物、环境变量、本地临时数据和数据库卷。
- 初始化 `backend/` FastAPI 后端工程，建立 `app/api`、`app/core`、`app/models`、`app/schemas`、`app/services`、`app/repositories` 和 `tests` 目录。
- 实现 `GET /api/health` 健康检查接口，返回中文状态信息。
- 添加后端依赖清单、pytest 配置和健康检查测试。
- 更新后端开发指南和 API 文档，记录后端启动、测试方式和 `/api/health` 响应结构。
- 明确后续每次代码、接口、数据字段、导入规则、页面结构或部署方式更新时，都必须同步更新 `docs/CHANGELOG.md`。
- 初始化本地 Git 仓库，使用 `main` 作为默认分支。
- 为当前阶段的空目录添加 `.gitkeep`，确保后续推送到 GitHub 后仍保留 `.github/workflows`、`data`、`deploy`、`frontend`、`scripts` 和 `tests` 目录。
- 更新 `.gitignore`，忽略 pytest 在 Windows 环境下可能生成的 `pytest-cache-files-*` 临时目录。
- 将”每次更新必须写入 `docs/CHANGELOG.md`、每次完成更新并验证后必须 Git 提交”写入 `AGENTS.md` 和 `docs/CODEX_WORKFLOW.md`。
- 全面更新 `docs/CODEX_WORKFLOW.md`，对齐 `docs/PROJECT_PLAN.md` 和 `AGENTS.md` 的最新内容：
  - **Section 3 通用系统提示词**：新增数据治理原则（指标字典优先、统一长表结构、来源追溯、质量报告完整字段、临时数据不进业务代码）、文档同步原则、Git 提交原则，要求 Codex 先阅读 AGENTS.md。
  - **M2 指标字典与数据模型**：补全指标字典 10 个字段（normal_range、color_scale、source_type 等），新增统一长表结构 12 个字段定义。
  - **M3 Excel 解析与质量报告**：长表结构补全 import_batch_id 等追溯字段，质量报告补全 10 个字段（导入批次 ID、跳过记录数、解析耗时、导入状态），要求测试 fixture 不硬编码临时目录路径。
  - **M4 地块 GeoJSON 解析**：明确引用 7.3 节地块编号标准化规则，列出 6 种需处理的地块编号情况，新增地块别名表和 Plot 完整字段。
  - **M5 后端 API**：接口从 8 个补全到 12 个（+summary、correlation、outliers、export），新增架构约束（路由只处理 HTTP、Pydantic schema 约束）。
  - **M6 前端工程**：基础组件从 5 个扩展到 13 个（补全 MetricSelector、DateSelector、RegionSelector、CesiumMapPanel、DataTable、ErrorState、ImportStatusTag、MetricValueTag）。
  - **M7 地图工作台**：新增无数据地块统一样式、异常地块明显提示要求。
  - **M9 数据导入中心**：质量报告显示字段完整对齐 7.4 节（10 个字段）。
  - **M12 相关性分析与异常识别**：异常类型从 3 种扩展到 8 种（对齐 8.7 节）。
  - **Section 5 任务模板**：新增数据与架构约束（5 条）、文档与 Git 约束（3 条）。
  - **Section 1.2 先文档后代码**：流程扩展为 10 步，加入阅读 AGENTS.md 和 Git 提交。
  - **Section 6 代码审查**：检查项从 10 条扩展到 12 条（长表结构、Pydantic schema、CHANGELOG、临时目录路径）。
  - **Section 11 控制点**：新增控制点 5「临时数据不进业务代码」。
