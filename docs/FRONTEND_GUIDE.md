# 前端开发指南

## 技术范围

前端按项目计划使用 Vue 3、TypeScript、Vite、Vue Router、Pinia、Ant Design Vue、ECharts、CesiumJS 和 Axios。本次初始化不创建前端工程，也不编写页面或组件代码。

## 目录建议

后续初始化前端后，建议在 `frontend/src/` 下按职责组织：

| 目录 | 用途 |
|---|---|
| `api/` | 后端接口封装 |
| `assets/` | 静态资源 |
| `components/` | 通用组件 |
| `composables/` | 组合式逻辑 |
| `constants/` | 常量与枚举 |
| `layouts/` | 页面布局 |
| `router/` | 路由配置 |
| `stores/` | Pinia 状态 |
| `styles/` | 全局样式和主题 |
| `types/` | TypeScript 类型 |
| `utils/` | 通用工具函数 |
| `views/` | 页面视图 |

## 开发约定

前端不直接解析 Excel，不直接依赖原始数据结构。页面应消费后端提供的标准化 API，并通过统一组件展示筛选器、地图、图表、表格和质量状态。

新增页面前，应先确认对应数据模型、接口草案和设计规范已经写入文档。
