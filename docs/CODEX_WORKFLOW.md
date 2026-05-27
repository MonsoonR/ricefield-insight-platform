# Codex 协作流程

## 当前定位

Codex 当前可以参与本项目开发，不再处于暂停状态。本文件记录 Codex 继续推进“稻田数字孪生演示平台”时的执行方式；通用规则以 `AGENTS.md` 和 `README.md` 为准。

当前主线是把系统功能、工程结构、接口契约、模拟数据和文档体系做扎实，不以大创答辩 PPT 作为核心开发任务。第一阶段仍聚焦场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析和系统说明六页闭环。

## 分支使用

截至本次流程梳理，当前活跃分支为 `claude/digital-twin-dev`。虽然分支名包含 Claude，但它已经是当前数字孪生主线的实际承接分支；Codex 后续可在该分支继续工作，不需要因为工具名称另起一条分支。

任务开始先执行：

```powershell
git status --short --branch
git log --oneline -n 8
```

分支处理规则：

- 用户没有指定新分支时，继续使用当前活跃分支。
- 工作区不干净时，先区分本次任务改动和既有改动，不能回滚或覆盖用户改动。
- 新建分支、切换基准分支、合并 `main`、回退历史、push 远端或创建 PR 前，先向用户确认。
- 不直接 push 到 `main`、`codex/digital-twin-clean` 或其他基准分支。

## 开发前检查

1. 阅读 `AGENTS.md`、`README.md` 和本文件。
2. 确认本次任务是否会触及技术栈、MVP 边界、数据模型、目录结构或导入契约；如会触及，先提出方案并等待确认。
3. 检查当前分支、未提交改动和最近提交记录。
4. 根据改动范围确定需要同步的专题文档和验证命令。
5. 行为变更优先补充或更新测试。

## 推荐任务顺序

1. 明确功能目标、数据字段、接口草案和页面结构。
2. 更新相关文档草稿。
3. 实现后端 schema、service、API 或前端服务、页面、组件。
4. 更新测试。
5. 更新 `docs/CHANGELOG.md`。
6. 运行验证。
7. 检查暂存范围并创建 commit。

## 必须先确认的事项

- 改变项目规划、技术栈、MVP 边界或目录结构。
- 修改数据模型、指标字典、API 契约、导入契约的结构性规则。
- 引入新依赖、新数据库方案、权限系统、复杂三维能力、自动报告、多项目管理或复杂空间分析。
- 恢复 Excel、GeoJSON、PDF、图片等文件导入主线，或加入真实客户数据文件。
- 改变当前分支策略、推送策略、发布策略或从其他分支重建主线。

## 验证命令

完整验证：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
npm --prefix frontend run build
```

仅文档变更且不涉及代码、配置、依赖、API 契约或运行时行为时，可以跳过完整验证，但最终回复必须说明原因。

涉及后端代码或 schema 时，至少运行 `backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。

涉及前端代码、组件、服务或路由时，至少运行受影响的前端服务测试与 `npm --prefix frontend run build`。

## 文档同步

| 变更类型 | 必须更新文档 |
|---|---|
| 数据字段、指标编码 | `docs/DATA_MODEL.md`、`docs/METRIC_DICTIONARY.md` |
| API 路径、请求或响应结构 | `docs/API.md` |
| 页面结构、路由 | `docs/FRONTEND_GUIDE.md`、`docs/USER_MANUAL.md` |
| 设计规范 | `docs/DESIGN_SYSTEM.md` |
| 模拟数据生成规则 | `docs/IMPORT_GUIDE.md` |
| 后端服务、依赖 | `docs/BACKEND_GUIDE.md` |
| 部署方式 | `docs/DEPLOYMENT.md` |
| 协作流程 | `README.md`、`AGENTS.md`、`docs/CLAUDE_WORKFLOW.md`、`docs/CODEX_WORKFLOW.md` |
| 任意实际更新 | `docs/CHANGELOG.md` |

`docs/IMPORT_GUIDE.md` 保留文件名，但当前内容是模拟场景与数据生成指南，不代表第一阶段恢复文件导入中心。

## 提交要求

每次完成实际更新并通过相应验证后提交 Git。提交前检查暂存范围，不提交虚拟环境、缓存、真实数据文件、构建产物或无关文件。

未经用户明确授权，不 push、不创建 PR、不改写已推送历史。
