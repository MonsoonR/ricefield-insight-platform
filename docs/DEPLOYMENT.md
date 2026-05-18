# 部署说明

## 本地演示

```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
npm --prefix frontend run dev
```

默认模式不需要数据库和数据文件。

## 构建

```powershell
npm --prefix frontend run build
```

## 可选 PostGIS

PostGIS 仅作为正式数据层保留。启用方式：

```powershell
$env:APP_DATA_BACKEND="postgres"
$env:DATABASE_URL="postgresql+psycopg://ricefield:ricefield@127.0.0.1:5432/ricefield"
backend\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
```

## 部署建议

- Nginx 托管前端静态资源。
- FastAPI 作为后端 API 服务。
- 生产环境通过 Docker Compose 管理前端、后端和数据库。
- 第一阶段演示优先使用默认模拟数据，减少环境依赖。
