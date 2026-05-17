# 前端开发指南

## 技术栈

Vue 3、TypeScript、Vite、Vue Router、Pinia、Ant Design Vue、ECharts、CesiumJS、Axios。

## 目录约定

| 目录 | 说明 |
|---|---|
| `src/api` | 后端 API 请求 |
| `src/pages` | 六页数字孪生演示页面 |
| `src/components/base` | 通用布局、地图、图表、表格、筛选器和状态组件 |
| `src/services` | 页面无关的转换、排序、状态计算 |
| `src/types` | API 和通用类型 |

## 页面路由

- `/overview`
- `/map-twin`
- `/plot-detail/:plotId?`
- `/metric-compare`
- `/warnings`
- `/system-docs`

不再提供 `/data-import`、`/outliers`、`/correlation`。

## API 使用

前端只请求标准化 API，不解析本地文件。新增页面应优先复用 `src/api/index.ts` 中的函数。

## 测试

当前服务层测试：

```powershell
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
```

构建：

```powershell
npm --prefix frontend run build
```
