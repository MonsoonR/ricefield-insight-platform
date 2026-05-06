# 稻田智研平台 Codex 协作开发指南

> 给个人开发者 + Codex 使用的分阶段开发指南。目标是让 Codex 每次只完成一个小而明确的任务，并且持续产出可审查、可运行、可测试、可维护的代码。

## 1. 使用原则

### 1.1 每次只让 Codex 做一个阶段的小任务

不要一次性让 Codex 完整开发整个系统。每次任务控制在一个明确范围内，例如：

- 初始化前端工程；
- 初始化后端工程；
- 创建项目目录结构；
- 实现 Excel 解析器；
- 实现指标字典；
- 实现一个 API；
- 实现一个前端页面；
- 给某个模块补测试；
- 根据已有代码更新文档。

推荐节奏：

```text
一个 Codex 任务 = 一个小目标 + 明确输入 + 明确输出 + 验收标准
```

### 1.2 先文档，后代码

每个阶段先让 Codex 阅读并更新文档，再开始写代码。

推荐顺序：

```text
1. 阅读 AGENTS.md（了解协作规则和技术边界）
2. 阅读 docs/PROJECT_PLAN.md
3. 阅读当前阶段相关文档
4. 说明本次改动计划
5. 修改代码
6. 添加测试
7. 运行检查
8. 更新文档（包括 CHANGELOG.md）
9. Git 提交
10. 总结改动和下一步
```

### 1.3 每次任务都要求 Codex 给出变更摘要

每次 Codex 完成任务后，要求它输出：

```text
1. 修改了哪些文件
2. 新增了哪些能力
3. 如何运行或测试
4. 当前还缺什么
5. 下一步建议做什么
```

### 1.4 每次任务都更新变更记录

每次代码、接口、数据字段、指标编码、导入规则、页面结构、设计规范或部署方式发生变化时，必须同步更新 `docs/CHANGELOG.md`。变更记录使用中文，按日期归档，写清楚“新增、修改、修复、文档更新、测试验证”等实际内容。

### 1.5 每次任务完成后提交 Git

每次任务完成并通过对应验证后，必须执行一次 Git 提交。提交前应先检查 `git status` 和暂存文件范围，确认没有提交 `.venv/`、`node_modules/`、缓存目录、临时样例数据或无关文件。

推荐顺序：

```text
1. 更新代码和文档
2. 更新 docs/CHANGELOG.md
3. 运行对应测试或检查
4. git status 检查改动范围
5. git add 精确暂存相关文件
6. git commit 写清楚本次变更
```

### 1.6 每次任务都要求最小可运行

不要接受“代码写了但跑不起来”的结果。每个阶段都应该能运行最小检查。

前端常用检查：

```bash
npm install
npm run dev
npm run build
npm run typecheck
npm run lint
```

后端常用检查：

```bash
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

如果项目使用 `pyproject.toml`，后端命令可改成对应包管理工具。

---

## 2. 推荐开发总顺序

```text
M0 项目初始化与文档框架
M1 后端基础工程
M2 数据字典与数据模型
M3 Excel 解析与导入质量报告
M4 地块 GeoJSON 解析
M5 后端 API
M6 前端基础工程与设计系统
M7 Cesium 地图工作台
M8 地块趋势图与指标筛选
M9 数据导入中心
M10 地块详情与指标对比
M11 数据库持久化
M12 相关性分析与异常识别
M13 Docker 部署与交付文档
```

第一轮 MVP 建议做到 M9 即可。M10 之后属于增强阶段。

---

## 3. Codex 通用系统提示词

每次开启新的 Codex 任务时，可以先贴下面这段作为通用约束。

```text
你正在开发”稻田智研平台”（RiceField Insight Platform）。这是一个面向研究所研究人员的智慧农田数据可视化与分析平台。

项目目标：
- 定期导入研究人员提供的 Excel 数据；
- 管理作物长势、成熟期预测、叶绿素、氮磷钾、pH、有机质、可溶性总盐分、叶面积指数、株高等指标；
- 结合地块 GeoJSON 和卫星地图展示农田地块；
- 支持指标筛选、日期筛选、地块着色、地块趋势、数据质量报告；
- 后续扩展相关性分析、异常识别、光谱/光照/遥感数据。

最终技术栈：
- 前端：Vue 3 + TypeScript + Vite + Vue Router + Pinia + Ant Design Vue + ECharts + CesiumJS + Axios
- 后端：FastAPI + Pydantic + pandas + openpyxl + SQLAlchemy + Alembic + Pytest
- MVP 数据层：标准化 JSON/CSV 或临时本地数据
- 正式数据层：PostgreSQL + PostGIS
- 部署：Docker Compose + Nginx

开发规则：
1. 每次只完成本次要求的范围，不要扩展到未要求的复杂功能。
2. 代码必须结构清晰，适合个人开发者长期维护。
3. 前端页面默认中文。
4. 所有接口返回和错误提示尽量中文可读。
5. Excel 数据解析不能静默丢弃异常，必须进入质量报告。
6. 新增指标必须进入指标字典。
7. 新增 API 必须同步更新接口文档。
8. 新增页面必须遵守设计规范。
9. 修改代码后给出运行命令、测试命令和变更摘要。
10. 优先保证 MVP 可运行，再考虑复杂扩展。

数据治理原则：
11. 所有指标进入系统前必须先进入指标字典。
12. Excel 解析后统一转换为长表结构，前端不得直接依赖 Excel 原始结构。
13. 每条数据记录必须支持来源追溯，至少保留：地块编号、指标编码、指标值、观测时间、导入批次ID、来源文件、来源工作表、来源单元格、数据质量标记。
14. 每次导入都必须生成质量报告，至少包括：成功记录数、缺失值数量、异常值数量、未匹配地块、错误单元格、跳过记录、解析耗时、导入状态。
15. 临时样例数据只用于理解数据结构，不得在业务代码、测试或文档中硬编码临时样例目录路径。

文档同步原则：
16. 新增或修改数据字段、指标编码、导入规则、API 响应结构、页面结构、设计规范或部署方式时，必须同步更新对应文档。
17. 每次有实际更新时，必须同步更新 docs/CHANGELOG.md，按日期归档，使用中文说明新增、修改、修复、文档更新和验证情况。
18. 优先更新：DATA_MODEL.md、METRIC_DICTIONARY.md、API.md、DESIGN_SYSTEM.md、IMPORT_GUIDE.md、CHANGELOG.md。

Git 提交原则：
19. 每次任务完成并通过验证后，必须执行 Git 提交。
20. 提交前检查 git status 和暂存范围，避免提交虚拟环境、缓存、临时样例数据或无关文件。
21. 不要引入未讨论的新技术栈或依赖。

请先阅读已有 README.md、docs/PROJECT_PLAN.md 和 AGENTS.md，再执行本次任务。
```

---

## 4. 分阶段提示词

### M0：初始化项目仓库

```text
请根据 docs/PROJECT_PLAN.md 初始化“稻田智研平台”的项目仓库结构。

要求：
1. 创建标准目录：
   - backend/
   - frontend/
   - data/
   - docs/
   - deploy/
   - scripts/
   - tests/
   - .github/workflows/
2. 创建 README.md，内容包括：项目简介、技术栈、目录结构、本地开发说明、文档入口。
3. 创建 docs/ 下的基础文档占位文件：
   - ARCHITECTURE.md
   - DATA_MODEL.md
   - METRIC_DICTIONARY.md
   - API.md
   - DESIGN_SYSTEM.md
   - FRONTEND_GUIDE.md
   - BACKEND_GUIDE.md
   - IMPORT_GUIDE.md
   - USER_MANUAL.md
   - DEPLOYMENT.md
   - CHANGELOG.md
4. 创建 .gitignore，排除 node_modules、Python 缓存、构建产物、环境变量、本地数据临时文件、数据库卷。
5. 不要实现业务代码。
6. 完成后说明创建了哪些文件，以及下一步建议。
```

验收标准：

```text
仓库结构清晰，README 能让新开发者理解项目，docs 文档框架完整。
```

---

### M1：初始化后端 FastAPI 工程

```text
请在 backend/ 下初始化 FastAPI 后端工程。

要求：
1. 使用 Python + FastAPI + Pydantic。
2. 建立目录结构：
   - backend/app/main.py
   - backend/app/api/
   - backend/app/core/
   - backend/app/models/
   - backend/app/schemas/
   - backend/app/services/
   - backend/app/repositories/
   - backend/tests/
3. 实现 GET /api/health，返回中文状态信息。
4. 添加 requirements.txt 或 pyproject.toml。
5. 添加 pytest 基础测试，测试 /api/health。
6. 更新 docs/BACKEND_GUIDE.md，说明后端目录结构和启动方式。
7. 更新 docs/API.md，记录 /api/health。

验收命令：
- 安装依赖；
- 启动 FastAPI；
- 运行 pytest。

完成后输出：修改文件、运行命令、测试结果、下一步建议。
```

---

### M2：建立指标字典与数据模型

```text
请为稻田智研平台建立第一版指标字典和数据模型。

指标包括：
- 作物长势
- 成熟期预测
- 叶绿素
- 氮
- 磷
- 钾
- pH
- 有机质
- 可溶性总盐分
- 叶面积指数
- 株高

要求：
1. 在 backend/app/core/ 或 backend/app/services/ 中创建指标字典定义。
2. 每个指标至少包含以下字段（参考 docs/PROJECT_PLAN.md 第 7.1 节）：
   - metric_code：指标编码（英文短码，如 crop_growth、chlorophyll）
   - metric_name：中文名称
   - category：指标类别（如 作物指标、土壤指标）
   - unit：单位
   - value_type：数值类型（float / int）
   - precision：小数位数
   - normal_range：正常范围（min, max）
   - color_scale：地图色阶（如 green-yellow-red）
   - description：指标说明
   - source_type：数据来源类型（如 excel、geojson、manual）
3. 建立统一长表结构（参考 PROJECT_PLAN 第 7.2 节），字段包括：
   - id：记录 ID
   - plot_id：地块 ID
   - plot_code：地块编号
   - metric_code：指标编码
   - value：指标值
   - unit：单位
   - observed_at：观测日期
   - import_batch_id：导入批次 ID
   - source_file：来源文件
   - raw_sheet：来源工作表
   - raw_cell：来源单元格
   - quality_flag：数据质量标记（normal / missing / outlier / error）
4. 建立 Pydantic schema：Metric、Plot、MetricObservation、ImportBatch、ImportIssue。
5. 数据结构优先服务 MVP，可以暂时不接数据库。
6. 增加测试，验证指标字典中包含上述所有指标。
7. 更新 docs/METRIC_DICTIONARY.md。
8. 更新 docs/DATA_MODEL.md。

完成后输出：指标编码列表、数据模型说明、测试命令、下一步建议。
```

---

### M3：实现 Excel 解析与质量报告

```text
请实现第一版 Excel 数据解析模块。

背景：
研究人员会定期提供多个 .xlsx 文件，每个文件可能对应一种或多种指标。系统需要读取 Excel，将数据转换为统一长表结构，并生成导入质量报告。

要求：
1. 在 backend/app/services/importer/ 下实现 Excel 解析服务。
2. 使用 pandas + openpyxl。
3. 输出统一长表结构（参考 docs/PROJECT_PLAN.md 第 7.2 节），每条记录必须包含：
   - id：记录 ID
   - plot_id：地块 ID
   - plot_code：地块编号
   - metric_code：指标编码
   - value：指标值
   - unit：单位
   - observed_at：观测日期
   - import_batch_id：导入批次 ID
   - source_file：来源文件
   - raw_sheet：来源工作表
   - raw_cell：来源单元格
   - quality_flag：数据质量标记（normal / missing / outlier / error）
4. 建立质量报告结构（参考 PROJECT_PLAN 第 7.4 节），至少包括：
   - 导入批次 ID
   - 文件名称
   - 成功记录数
   - 缺失值数量
   - 异常值数量
   - 未匹配地块列表
   - 错误单元格列表
   - 跳过记录数
   - 解析耗时（毫秒）
   - 导入状态（success / partial / failed）
5. 不要静默丢弃异常数据，所有异常必须进入质量报告。
6. 支持读取 data/imports/ 下的示例 Excel。
7. 添加单元测试。
8. 更新 docs/IMPORT_GUIDE.md 和 docs/DATA_MODEL.md。

如果当前没有真实 Excel 文件，请创建一个最小示例文件或测试 fixture，用于验证解析流程。测试 fixture 应放在 tests/ 目录下，不要硬编码临时样例目录路径。

完成后输出：解析流程、质量报告结构、测试结果、下一步建议。
```

---

### M4：实现地块 GeoJSON 解析

```text
请实现地块 GeoJSON 解析模块。

要求：
1. 支持读取 data/geojson/ 下的地块 GeoJSON 文件。
2. 解析地块编号（plot_code）、地块别名（alias）、所属区域（东区/西区）、geometry。
3. 建立地块编号标准化函数，参考 docs/PROJECT_PLAN.md 第 7.3 节，处理以下情况：
   - 不同写法的同一地块（如 21A 和 21A-1）
   - 东区、西区编号差异
   - 重复编号
   - 中文乱码编号
   - Excel 中存在但 GeoJSON 中无法定位的地块
   - GeoJSON 中存在但 Excel 中暂无数据的地块
4. 建立地块别名表（plot_aliases），支持一对多别名映射。
5. 输出 Plot 数据结构，包含：plot_id、plot_code、aliases、region、geometry、status。
6. 生成未匹配或重复地块报告。
7. 添加测试。
8. 更新 docs/DATA_MODEL.md 和 docs/IMPORT_GUIDE.md。

完成后输出：解析结果结构、标准化规则、测试结果、下一步建议。
```

---

### M5：实现 MVP 后端 API

```text
请实现稻田智研平台 MVP 所需的后端 API。

接口包括（参考 docs/PROJECT_PLAN.md 第 11 节）：
1. GET /api/health — 健康检查
2. GET /api/metrics — 获取指标字典
3. GET /api/plots — 获取地块列表
4. GET /api/dates — 获取可用观测日期
5. GET /api/imports — 获取导入批次列表
6. GET /api/imports/{id}/report — 获取导入质量报告
7. GET /api/map/layers — 获取地图图层数据
8. GET /api/plots/{plotId}/summary — 获取地块摘要
9. GET /api/plots/{plotId}/series — 获取地块趋势
10. GET /api/analysis/correlation — 获取相关性分析结果（MVP 阶段可先返回占位结构）
11. GET /api/analysis/outliers — 获取异常识别结果（MVP 阶段可先返回占位结构）
12. GET /api/export/report — 导出分析结果（MVP 阶段可先返回占位结构）

要求：
1. API 可以先读取本地标准化 JSON/CSV 或内存数据。
2. 不要直接在路由函数里写复杂业务逻辑，业务逻辑放到 service 层。
3. 路由函数只处理 HTTP 输入输出。
4. 所有接口请求和响应使用 Pydantic schema 约束。
5. 返回字段命名稳定，不随 Excel 原始结构变化。
6. 错误信息中文可读。
7. 添加 API 测试。
8. 更新 docs/API.md。

完成后输出：接口列表、请求示例、返回示例、测试结果、下一步建议。
```

---

### M6：初始化前端 Vue 工程与设计系统

```text
请在 frontend/ 下初始化 Vue 3 前端工程。

技术栈：
- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Ant Design Vue
- ECharts
- CesiumJS
- Axios

要求：
1. 建立基础目录：
   - src/api/
   - src/assets/
   - src/components/
   - src/components/base/
   - src/layouts/
   - src/pages/
   - src/router/
   - src/stores/
   - src/styles/
   - src/types/
   - src/utils/
2. 配置 Ant Design Vue。
3. 配置基础主题 token。
4. 创建主布局：左侧菜单 + 顶部标题 + 内容区。
5. 创建页面路由：
   - 概览
   - 地图分析
   - 数据导入
   - 指标对比
   - 系统文档
6. 创建基础组件（参考 docs/PROJECT_PLAN.md 第 12 节）：
   - PageContainer：页面容器，统一标题、间距、布局
   - FilterBar：通用筛选栏
   - MetricSelector：指标选择器
   - DateSelector：日期选择器
   - RegionSelector：区域选择器（全部/东区/西区）
   - ChartCard：图表卡片容器
   - CesiumMapPanel：地图面板容器
   - DataTable：统一数据表格
   - StatusTag：状态标签（正常/异常/缺失/无数据）
   - EmptyState：空状态占位
   - ErrorState：错误状态占位
   - ImportStatusTag：导入状态标签
   - MetricValueTag：指标值标签
7. 更新 docs/DESIGN_SYSTEM.md 和 docs/FRONTEND_GUIDE.md。
8. 确保 npm run build 可以通过。

完成后输出：目录结构、页面列表、运行命令、下一步建议。
```

---

### M7：实现 Cesium 地图工作台第一版

```text
请实现“地图分析”页面第一版。

要求：
1. 使用 CesiumJS 创建地图容器。
2. 支持加载地块 GeoJSON。
3. 地块显示为边界面。
4. 支持按区域筛选：全部、东区、西区。
5. 支持按指标筛选。
6. 支持按日期筛选。
7. 地块根据当前指标值着色。
8. 点击地块后显示右侧信息面板。
9. 信息面板显示：地块编号、区域、指标值、日期、数据来源。
10. 无数据地块使用统一样式（灰色或虚线边框），与有数据地块明确区分。
11. 异常地块使用明显提示样式（如红色边框或高亮闪烁）。
12. 暂时不要实现复杂三维地形、3D Tiles、遥感时序动画。
13. 地图相关逻辑拆分为 composable 或 service，避免全部堆在页面组件中。
14. 更新 docs/FRONTEND_GUIDE.md 和 docs/USER_MANUAL.md。

完成后输出：地图实现说明、数据依赖、运行命令、下一步建议。
```

---

### M8：实现地块趋势图联动

```text
请在地图分析页面中加入地块趋势图联动。

要求：
1. 点击地块后调用 /api/plots/{plotId}/series。
2. 使用 ECharts 展示当前地块的指标趋势。
3. 支持切换指标后更新趋势图。
4. 图表显示单位、日期、数据来源提示。
5. 无数据时显示统一 EmptyState。
6. 将 ECharts 封装为可复用组件。
7. 更新 docs/USER_MANUAL.md 和 docs/API.md。

完成后输出：新增组件、接口调用方式、测试方式、下一步建议。
```

---

### M9：实现数据导入中心

```text
请实现“数据导入中心”页面。

要求：
1. 展示导入批次列表。
2. 显示每个批次的导入时间、文件数量、成功记录数、问题数量、状态。
3. 支持点击批次查看质量报告（参考 PROJECT_PLAN 第 7.4 节）。
4. 质量报告显示：导入批次 ID、文件名称、成功记录数、缺失值数量、异常值数量、未匹配地块列表、错误单元格列表、跳过记录数、解析耗时、导入状态（success / partial / failed）。
5. 问题列表可以按类型筛选（缺失值、异常值、未匹配地块、错误单元格）。
6. 所有状态标签使用统一组件。
7. 暂时可以只展示后端返回的数据，不需要做前端上传。
8. 更新 docs/USER_MANUAL.md。

完成后输出：页面功能说明、接口依赖、运行命令、下一步建议。
```

---

### M10：实现地块详情与指标对比

```text
请实现地块详情页和指标对比页的第一版。

要求：
1. 地块详情页展示：地块基础信息、地图定位、多个指标趋势、数据来源。
2. 指标对比页支持：选择多个地块、选择一个指标、展示折线趋势对比。
3. 使用 ECharts。
4. 筛选器使用统一 FilterBar。
5. 图表容器使用统一 ChartCard。
6. 无数据和错误状态使用统一组件。
7. 更新 docs/USER_MANUAL.md 和 docs/API.md。

完成后输出：页面说明、组件复用情况、接口依赖、下一步建议。
```

---

### M11：引入 PostgreSQL + PostGIS

```text
请为项目引入 PostgreSQL + PostGIS 持久化方案。

要求：
1. 设计数据库表：
   - metrics
   - plots
   - plot_aliases
   - metric_observations
   - import_batches
   - import_issues
2. 使用 SQLAlchemy 定义模型。
3. 使用 Alembic 管理迁移。
4. 将 Excel 和 GeoJSON 导入结果写入数据库。
5. API 从数据库读取数据。
6. 保留 MVP 本地数据模式作为开发 fallback。
7. 添加数据库相关测试。
8. 更新 docs/DATA_MODEL.md、docs/BACKEND_GUIDE.md、docs/DEPLOYMENT.md。

完成后输出：数据库表说明、迁移命令、测试命令、下一步建议。
```

---

### M12：相关性分析与异常识别

```text
请实现相关性分析与异常识别的第一版。

要求：
1. 相关性分析支持选择两个指标，返回样本量、相关系数、散点图数据。
2. 异常识别支持以下类型（参考 PROJECT_PLAN 第 8.7 节）：缺失值、极端值、同区域偏离、趋势突变、连续多期异常、数据格式异常、地块编号无法匹配、指标单位异常。
3. 后端提供：
   - GET /api/analysis/correlation
   - GET /api/analysis/outliers
4. 前端提供：
   - 相关性分析页面
   - 异常识别页面
5. 异常结果可以跳转到地块详情。
6. 分析结果必须显示样本量和说明，避免误导研究人员。
7. 更新 docs/API.md 和 docs/USER_MANUAL.md。

完成后输出：分析方法说明、接口说明、页面说明、下一步建议。
```

---

### M13：Docker 部署与交付

```text
请为项目添加 Docker Compose 部署方案。

要求：
1. backend Dockerfile。
2. frontend Dockerfile。
3. docker-compose.yml，包含：
   - frontend
   - backend
   - postgres/postgis
   - nginx
4. Nginx 配置：前端静态资源 + API 反向代理。
5. 数据目录挂载。
6. 数据库备份说明。
7. 更新 docs/DEPLOYMENT.md。
8. 添加 GitHub Actions：
   - 后端测试
   - 前端构建

完成后输出：部署命令、服务说明、检查方式、下一步建议。
```

---

## 5. 每次给 Codex 的任务模板

可以复制下面模板，每次只替换“本次任务”。

```text
请在当前仓库中执行一个小任务。

项目背景：
这是”稻田智研平台”，技术栈为 Vue 3 + TypeScript + Vite + Ant Design Vue + ECharts + CesiumJS + FastAPI。项目面向研究所研究人员，用于 Excel 数据导入、地块地图展示、指标趋势分析和数据质量报告。

本次任务：
【在这里写清楚一个小任务】

范围限制：
1. 只做本次任务，不要扩展额外功能。
2. 不要重构无关文件。
3. 不要引入未讨论的新技术。
4. 页面中文优先。
5. 代码结构要适合个人开发者维护。

数据与架构约束：
6. Excel 解析后统一为长表结构，前端不直接依赖 Excel 原始结构。
7. 每次导入必须生成质量报告，不能隐藏缺失值、异常值、未匹配地块或解析错误。
8. 后端路由只处理 HTTP 输入输出，业务逻辑放在 service 层。
9. 请求、响应和数据结构使用 Pydantic schema 约束。
10. 不要在业务代码、测试或文档中硬编码临时样例目录路径。

文档与 Git 约束：
11. 新增或修改数据字段、指标编码、导入规则、API 响应结构、页面结构时，必须同步更新对应文档。
12. 每次有实际更新时，必须同步更新 docs/CHANGELOG.md。
13. 任务完成并通过验证后，必须执行 Git 提交。

交付要求：
1. 修改必要代码。
2. 添加或更新测试。
3. 更新相关文档（包括 CHANGELOG.md）。
4. 给出运行命令和测试命令。
5. 最后输出变更摘要、风险点、下一步建议。

验收标准：
【写清楚如何判断完成】
```

---

## 6. 让 Codex 做代码审查的提示词

```text
请审查当前代码，不要直接大规模重写。

重点检查：
1. 是否符合 docs/PROJECT_PLAN.md 和 AGENTS.md 的技术栈和阶段目标；
2. 前端组件是否职责清晰；
3. 后端路由是否把业务逻辑放在 service 层，路由函数只处理 HTTP 输入输出；
4. Excel 解析是否会静默丢弃异常数据；
5. 数据是否转换为统一长表结构，是否支持来源追溯；
6. API 字段命名是否稳定，请求和响应是否使用 Pydantic schema；
7. 中文错误提示是否清楚；
8. 是否缺少测试；
9. 是否缺少文档更新（特别是 CHANGELOG.md）；
10. 是否引入了不必要的复杂依赖或新技术栈；
11. 是否存在安全或部署风险；
12. 是否在业务代码或测试中硬编码了临时样例目录路径。

请输出：
- 问题清单；
- 每个问题的严重程度；
- 建议修改方式；
- 建议优先级；
- 不要直接修改代码，除非我明确要求。
```

---

## 7. 让 Codex 修 Bug 的提示词

```text
请修复下面这个问题。

问题描述：
【粘贴错误现象、报错信息、截图说明或复现步骤】

要求：
1. 先定位原因；
2. 说明涉及哪些文件；
3. 只修改和问题直接相关的代码；
4. 添加或更新测试；
5. 说明如何验证修复成功；
6. 不要引入新技术栈；
7. 不要重构无关模块。

完成后输出：
- 根因；
- 修改内容；
- 验证方式；
- 后续风险。
```

---

## 8. 让 Codex 更新文档的提示词

```text
请根据当前代码更新项目文档。

要求：
1. 阅读 README.md 和 docs/ 下已有文档。
2. 对照当前代码，补齐不准确或缺失的说明。
3. 更新相关文档，不要新增重复文档。
4. 文档中文优先。
5. 保持结构清晰，适合个人开发者和后续维护人员阅读。
6. 如果发现代码和文档不一致，请列出不一致点。

完成后输出：
- 更新了哪些文档；
- 补充了哪些内容；
- 代码和文档仍有哪些不一致。
```

---

## 9. 个人开发者使用 Codex 的建议流程

### 每天开发前

```text
1. 查看 GitHub Issues
2. 选择一个小任务
3. 写清楚验收标准
4. 把任务交给 Codex
5. 只接受可运行、可测试、可解释的结果
```

### Codex 完成后

```text
1. 看变更文件
2. 看是否改了无关内容
3. 本地运行测试
4. 本地启动前后端
5. 检查页面和接口
6. 更新 Issue 状态
7. 提交 Git commit
```

### 每个阶段结束后

```text
1. 让 Codex 做一次代码审查
2. 让 Codex 更新文档
3. 自己跑一遍验收流程
4. 打一个 Git tag 或记录版本
5. 再进入下一阶段
```

---

## 10. GitHub Issue 拆分建议

MVP 阶段建议建立以下 Issues：

```text
# M0 项目初始化
- 初始化仓库结构
- 创建 README 和 docs 文档框架

# M1 后端基础
- 初始化 FastAPI 工程
- 实现 /api/health
- 添加后端测试

# M2 数据模型
- 建立指标字典
- 建立 Pydantic 数据模型
- 编写指标字典文档

# M3 Excel 导入
- 实现 Excel 解析服务
- 实现导入质量报告
- 添加 Excel 解析测试

# M4 地块数据
- 实现 GeoJSON 解析
- 实现地块编号标准化
- 实现地块别名规则

# M5 API
- 实现指标、地块、日期 API
- 实现导入批次和质量报告 API
- 实现地块趋势 API

# M6 前端基础
- 初始化 Vue 3 工程
- 配置 Ant Design Vue
- 创建主布局和路由
- 创建基础组件

# M7 地图工作台
- 实现 Cesium 地图容器
- 加载地块 GeoJSON
- 实现地块着色
- 实现地块点击详情

# M8 趋势联动
- 实现地块趋势图
- 实现地图和图表联动

# M9 数据导入中心
- 实现导入批次列表
- 实现质量报告详情
```

---

## 11. 最重要的控制点

### 控制点 1：不要让 Codex 一次做太多

错误示例：

```text
帮我把整个智慧农田平台做出来。
```

正确示例：

```text
请只实现 backend/app/services/importer/excel_importer.py，用 pandas 读取一个示例 Excel，并输出统一长表结构和质量报告。添加测试，不要修改前端。
```

### 控制点 2：每次都要有验收标准

没有验收标准，Codex 容易写出看起来完整但无法验证的代码。

### 控制点 3：文档和代码同步

每次新建 API、新增指标、新增页面，都要求更新文档。

### 控制点 4：先做 MVP 闭环

第一版只追求：

```text
Excel 导入 → 数据质量报告 → API → Cesium 地图 → 地块着色 → 点击趋势
```

这个闭环完成后，再做数据库、相关性分析、异常识别、部署。

### 控制点 5：临时数据不进业务代码

临时样例数据只用于理解数据结构和验证导入规则。业务代码、测试夹具、文档规范中不得硬编码临时样例目录路径（如 `data/raw/sample_2025.xlsx`）。样例数据的结论应沉淀为指标字典、数据模型、导入契约、质量规则或测试夹具设计。

### 控制点 6：你负责验收，Codex 负责实现

Codex 可以写代码、补测试、改文档。你需要负责判断：

- 是否符合项目目标；
- 是否跑得起来；
- 是否容易维护；
- 是否对研究人员真的有用。

---

## 12. 推荐第一条 Codex 任务

建议你下一步直接把下面这段发给 Codex：

```text
请根据 docs/PROJECT_PLAN.md 初始化“稻田智研平台”的项目仓库结构。

本次只做项目初始化，不实现业务代码。

要求：
1. 创建目录：backend、frontend、data、docs、deploy、scripts、tests、.github/workflows。
2. 创建 README.md，说明项目背景、技术栈、目录结构、本地开发方式、文档入口。
3. 创建 docs 下的基础文档：ARCHITECTURE.md、DATA_MODEL.md、METRIC_DICTIONARY.md、API.md、DESIGN_SYSTEM.md、FRONTEND_GUIDE.md、BACKEND_GUIDE.md、IMPORT_GUIDE.md、USER_MANUAL.md、DEPLOYMENT.md、CHANGELOG.md。
4. 创建 .gitignore，排除 node_modules、Python 缓存、构建产物、环境变量、本地临时数据、数据库卷。
5. README 和文档全部中文优先。
6. 不要引入未讨论的新技术。
7. 不要写前后端业务代码。

完成后请输出：
- 创建了哪些文件；
- 每个目录的用途；
- 下一步建议做什么。
```
