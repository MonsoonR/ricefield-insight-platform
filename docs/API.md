# API 文档

## 设计原则

API 返回字段命名应稳定，错误信息中文可读。路由函数只处理 HTTP 输入输出，业务逻辑放在服务层。所有接口响应应使用 Pydantic schema 约束结构。

## 已实现接口

### GET /api/health

用途：后端服务健康检查。

请求参数：无。

响应示例：

```json
{
  "status": "ok",
  "message": "稻田智研平台后端服务运行正常"
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| `status` | string | 服务状态，当前正常时返回 `ok` |
| `message` | string | 中文状态说明 |

## 初步接口规划

| 接口 | 用途 | 状态 |
|---|---|---|
| `GET /api/health` | 健康检查 | 已实现 |
| `GET /api/metrics` | 获取指标字典 | 规划中 |
| `GET /api/plots` | 获取地块列表 | 规划中 |
| `GET /api/dates` | 获取可用观测日期 | 规划中 |
| `GET /api/imports` | 获取导入批次列表 | 规划中 |
| `GET /api/imports/{id}/report` | 获取导入质量报告 | 规划中 |
| `GET /api/map/layers` | 获取地图图层数据 | 规划中 |
| `GET /api/plots/{plotId}/summary` | 获取地块摘要 | 规划中 |
| `GET /api/plots/{plotId}/series` | 获取地块趋势 | 规划中 |
| `GET /api/analysis/correlation` | 获取相关性分析结果 | 规划中 |
| `GET /api/analysis/outliers` | 获取异常识别结果 | 规划中 |
| `GET /api/export/report` | 导出分析结果 | 规划中 |

## 当前状态

当前仅完成 FastAPI 工程初始化和健康检查接口。后续开发业务 API 前，应先补充请求参数、响应示例、错误码和分页规则，并同步更新数据模型、指标字典和导入规则文档。
