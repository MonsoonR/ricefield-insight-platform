# Claude 协作流程

## 当前定位

本文件记录 Claude 参与本项目时的协作注意事项，不再声明“Claude 优先”或“Codex 暂停”。项目当前真实开发方式是：Claude 和 Codex 都可以继续推进同一条数字孪生主线，统一遵守 `AGENTS.md`、`README.md` 的开发协作要求和当前活跃 Git 分支。

当前开发目标仍是把“稻田数字孪生演示平台”的系统功能和工程结构做扎实，不以大创答辩 PPT 作为当前核心开发任务。大创答辩材料只作为后续展示场景，不主导功能开发。

## 项目基准

- 项目身份：稻田智研平台（RiceField Insight Platform）。
- 第一阶段范围：场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析、系统说明六页闭环。
- 默认数据：后端程序生成 `demo-ricefield-2025` 场景，包含 8 个程序生成地块、11 个指标、45 天观测和预警事件。
- 可选正式层：PostgreSQL + PostGIS，复用同一套 API 契约。
- 第一阶段不恢复 Excel、GeoJSON、PDF、图片等文件导入主线，不恢复导入中心和导入报告接口。

## 分支使用

截至本次流程梳理，当前活跃分支是 `claude/digital-twin-dev`，它承接 `codex/digital-twin-clean` 之后的数字孪生开发主线。后续任务默认继续使用当前活跃分支，不按工具拆分新的 Claude/Codex 分支。

每次任务开始先执行：

```powershell
git status --short --branch
git log --oneline -n 8
```

处理原则：

- 如果用户没有要求切换分支，继续在当前活跃分支工作。
- 如果工作区有未提交改动，先判断是否与本次任务相关；不得覆盖用户或其他工具的改动。
- 如果需要从 `main`、`codex/digital-twin-clean` 或其他分支重新开线，先说明原因并等待用户确认。
- 不直接 push 到 `main`、`codex/digital-twin-clean` 或其他受保护/基准分支。
- push、创建 PR、回合并基准分支、强制推送都必须先得到用户明确授权。

## 必须先确认的事项

以下事项不要直接修改，先提出建议并等待用户确认：

- 项目规划、技术栈、目录结构、MVP 边界。
- 数据模型、指标字典、API 契约、导入契约的结构性调整。
- 新增未讨论依赖、数据库方案、权限系统、复杂三维能力、自动报告、多项目管理或复杂空间分析。
- 恢复 Excel、GeoJSON、PDF、图片等文件导入主线，或新增真实数据文件。
- 改变当前分支策略、远端推送策略或发布流程。

## 当前禁止事项

- 不得提交真实客户数据文件、真实 Excel、真实 GeoJSON、客户 PDF、客户图片或可识别来源的数据材料。
- 不得在前端直接解析原始 Excel、GeoJSON、PDF 或图片。
- 不得把系统改回旧的数据导入平台。
- 不得新增 `/api/imports`、`/api/imports/{id}/report`、`/api/export/report` 等第一阶段已移除接口，除非用户确认新的阶段目标。
- 不得删除或绕过现有 docs 基准。
- 不得使用 `git reset --hard`、强制推送或覆盖他人改动，除非用户明确要求。

## 每次任务前检查

1. 阅读 `AGENTS.md`、`README.md` 和本文件。
2. 检查当前分支、工作区状态和最近提交。
3. 明确本次任务是否只改文档，还是涉及代码、接口、数据模型或页面行为。
4. 涉及数据字段、指标、API、页面结构、设计规范、模拟数据规则或部署方式时，先确定要同步的专题文档。
5. 行为变更优先补充或更新对应测试。

## 每次任务后收尾

1. 同步更新相关文档。
2. 必须更新 `docs/CHANGELOG.md`，按日期记录新增、修改、删除、文档更新和验证情况。
3. 运行与改动范围匹配的验证命令。
4. 用 `git status --short` 检查暂存范围，排除虚拟环境、缓存、真实数据文件、构建产物和无关文件。
5. 完成实际更新并通过相应验证后创建 Git commit。
6. 未经用户确认不推送远端、不创建 PR。

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

仅文档变更且不涉及代码、配置、依赖、API 契约或运行时行为时，可以跳过完整验证，但最终回复必须明确说明。

涉及后端代码或 schema 时，至少运行 `backend\.venv\Scripts\python.exe -m pytest backend\tests -q`。

涉及前端代码、组件、服务或路由时，至少运行受影响的前端服务测试与 `npm --prefix frontend run build`。

## 文档同步规则

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

文档先于实现：架构、数据模型、API 契约和页面结构变更，先写或更新文档再写代码。

## Git commit 规则

- 提交前用 `git status --short` 检查暂存范围。
- 不提交 `.venv/`、`venv/`、`env/`、Python/pytest 缓存、`node_modules/`、`dist/`、`build/`、真实数据文件、`.env` 或无关修改。
- commit message 使用中文或英文均可，建议格式：`feat: ...`、`fix: ...`、`docs: ...`、`refactor: ...`、`chore: ...`。
- 每次实际更新至少包含一个对应的 `docs/CHANGELOG.md` 条目。
- 不使用 `--amend` 修改已推送提交，不使用 `--no-verify` 跳过 hook，除非用户明确要求。

## 最终回复

任务结束时说明：修改摘要、修改文件、CHANGELOG 条目、验证命令和结果、commit hash、是否 push。若未测试、未 commit 或未 push，明确原因。
