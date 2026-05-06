# 后端开发指南

## 技术范围

后端使用 Python、FastAPI、Pydantic 和 Pytest 初始化。当前阶段仅包含基础工程结构和健康检查接口，Excel 解析、GeoJSON 加载、指标导入和质量报告仍按 MVP 后续任务逐步实现。

## 目录结构

后端代码位于 `backend/`：

| 目录或文件 | 用途 |
|---|---|
| `app/main.py` | FastAPI 应用入口，负责创建应用并注册路由 |
| `app/api/` | 路由定义和 HTTP 输入输出 |
| `app/core/` | 配置、日志、异常等基础能力 |
| `app/models/` | 数据库模型，当前 MVP 初始阶段暂未启用 |
| `app/schemas/` | Pydantic 请求和响应结构 |
| `app/services/` | 业务逻辑 |
| `app/repositories/` | 数据访问，当前 MVP 初始阶段暂未启用 |
| `tests/` | Pytest 测试 |
| `requirements.txt` | 后端依赖清单 |
| `pytest.ini` | 后端测试配置 |

## 本地启动

在仓库根目录执行：

```powershell
C:\Users\Monso\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m venv --without-pip backend\.venv
C:\Users\Monso\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip --python backend\.venv\Scripts\python.exe install -r backend\requirements.txt
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

如果本机 `python` 可用，也可以使用：

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

启动后访问：

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/docs`

## 测试

在仓库根目录执行：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests
```

## 开发约定

路由函数保持薄层，只做参数接收、调用服务和返回响应。Excel / GeoJSON 解析、地块匹配、指标映射、质量检查和报告生成应放在服务或数据处理模块中。

所有接口响应优先使用 Pydantic schema 约束结构。所有错误信息应尽量中文可读，方便项目维护人员定位数据问题。
