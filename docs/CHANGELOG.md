# 变更记录

## 2026-05-06

### 新增

- 初始化项目仓库目录结构，创建中文优先的 README 和基础文档入口。
- 初始化 `backend/` FastAPI 后端工程，建立 `app/api`、`app/core`、`app/models`、`app/schemas`、`app/services`、`app/repositories` 和 `tests` 目录。
- 实现 `GET /api/health` 健康检查接口，返回中文状态信息。
- 添加后端依赖清单、pytest 配置和健康检查测试。
- 建立第一版指标字典 `backend/app/core/metric_dictionary.py`，包含作物长势、成熟期预测、叶绿素、氮、磷、钾、pH、有机质、可溶性总盐分、叶面积指数、株高 11 个指标。
- 建立 Pydantic 数据模型 `backend/app/schemas/data_model.py`，包含 `Metric`、`Plot`、`MetricObservation`、`ImportBatch`、`ImportIssue`，并定义统一长表追溯字段和质量标记。
- 添加指标字典测试，验证第一版指标编码、字典必备字段和长表追溯字段。

### 修改

- 更新 `.gitignore`，忽略依赖、缓存、构建产物、环境变量、本地临时数据、数据库卷和 Windows 环境下可能生成的 `pytest-cache-files-*` 临时目录。
- 将“每次更新必须写入 `docs/CHANGELOG.md`、每次完成更新并验证后必须 Git 提交”写入 `AGENTS.md` 和 `docs/CODEX_WORKFLOW.md`。
- 全面更新 `docs/CODEX_WORKFLOW.md`，对齐 `docs/PROJECT_PLAN.md` 和 `AGENTS.md` 的数据治理、MVP 边界、文档同步、Git 提交和代码审查约束。

### 文档更新

- 更新后端开发指南和 API 文档，记录后端启动、测试方式和 `/api/health` 响应结构。
- 更新 `docs/METRIC_DICTIONARY.md`，补齐第一版指标编码、单位、类型、精度、正常范围、色阶和来源类型。
- 更新 `docs/DATA_MODEL.md`，补齐 `Metric`、`Plot`、`MetricObservation`、`ImportBatch`、`ImportIssue` 字段说明和来源追溯规则。

### 验证

- 已通过 `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_metric_dictionary.py`。
- 已通过 `backend\.venv\Scripts\python.exe -m pytest backend\tests`。
