# 后端开发指南

## 技术栈

FastAPI、Pydantic、SQLAlchemy、Alembic、Pytest。

第一阶段后端不依赖 pandas 或 openpyxl，不实现 Excel 解析。

## 启动

```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

默认使用程序生成模拟场景。

## 数据后端

| 模式 | 说明 |
|---|---|
| 默认 | `MvpDataStore` 生成 `demo-ricefield-2025` |
| `APP_DATA_BACKEND=postgres` | `DatabaseDataStore` 从 PostgreSQL + PostGIS 读取兼容数据 |

## 开发规则

- 路由函数只接收参数、调用 service、返回 schema。
- 业务逻辑放在 `app/services`。
- 响应结构定义在 `app/schemas`。
- 新增字段必须同步更新 `docs/DATA_MODEL.md` 和 `docs/API.md`。
- 新增行为先写 Pytest。

## 测试

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
```
