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
- 将“每次更新必须写入 `docs/CHANGELOG.md`、每次完成更新并验证后必须 Git 提交”写入 `AGENTS.md` 和 `docs/CODEX_WORKFLOW.md`。
