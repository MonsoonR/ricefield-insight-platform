# Claude 协作流程

## 当前阶段说明

当前阶段全程优先使用 Claude 进行开发，暂不使用 Codex。新的工作主线是把"稻田数字孪生演示平台"的系统功能和工程结构做扎实，而不是制作大创答辩 PPT。大创答辩材料保留为后续展示场景，但不主导当前功能开发。

## 项目基准

- 项目身份：稻田智研平台（RiceField Insight Platform）。
- 第一阶段范围：场景驾驶舱、Cesium 地图孪生、地块画像、指标对比、预警分析、系统说明六页闭环。
- 默认数据：后端程序生成 `demo-ricefield-2025` 场景，包含 8 个程序生成地块、11 个指标、45 天观测和预警事件。
- 可选正式层：PostgreSQL + PostGIS，复用同一套 API 契约。

## 当前禁止事项

- 不得恢复 Excel、GeoJSON、PDF、图片等文件导入主线。
- 不得新增数据导入中心、导入报告或文件导出接口（`/api/imports`、`/api/imports/{id}/report`、`/api/export/report`）。
- 不得提交真实客户数据文件、真实 Excel、真实 GeoJSON、客户 PDF 或图片。
- 不得删除或绕过现有 docs 基准（`AGENTS.md`、`docs/PROJECT_PLAN.md`、`docs/ARCHITECTURE.md`、`docs/DATA_MODEL.md`、`docs/API.md` 等）。
- 不得把系统改回旧的数据导入平台。
- 当前阶段不制作大创答辩 PPT，不要把答辩材料作为开发产出。
- 不引入未讨论的新技术或新依赖。
- 不在没有用户确认的情况下推送到远端 `main` 或修改受保护分支。

## Claude 分支创建方式

Claude 全程在 `claude/digital-twin-dev` 分支上工作，从基准分支 `codex/digital-twin-clean` 创建，不直接基于 `main`。

```powershell
git fetch origin
git checkout codex/digital-twin-clean
git pull --ff-only origin codex/digital-twin-clean
git checkout -b claude/digital-twin-dev
```

如果 `codex/digital-twin-clean` 不可用或无法拉取，停止并向用户说明原因，禁止从旧 `main` 分支创建。

如果 `claude/digital-twin-dev` 已存在，直接切换并保持同步：

```powershell
git checkout claude/digital-twin-dev
git pull --ff-only origin claude/digital-twin-dev
```

## 每次任务前检查清单

1. 阅读 `AGENTS.md` 和本文件，确认禁止事项未被踩到。
2. 运行 `git status --short`，确认工作区是否干净，不要覆盖用户未提交改动。
3. 确认当前分支是 `claude/digital-twin-dev`。
4. 根据任务范围，提前确定需要更新的代码、测试和文档。
5. 行为变更先写或更新 Pytest / 前端服务测试。
6. 涉及数据字段、指标、API、页面结构、部署方式时，先写文档草稿再写实现。

## 每次任务后收尾清单

1. 同步更新相关文档（参见"文档同步规则"）。
2. 更新 `docs/CHANGELOG.md`，按当日条目记录新增、修改、删除、文档更新和验证情况。
3. 运行所有相关验证命令并确认通过。
4. 检查 `git status --short`，确认暂存范围正确，没有虚拟环境、缓存、真实数据文件、构建产物或无关文件。
5. 创建 Git commit。
6. 如远端安全且用户已授权，推送到远端开发分支。
7. 给出最终回复，按"Claude 最终回复格式"输出。

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

仅文档变更（不涉及代码、配置、依赖）时，可以跳过完整验证，但必须在最终回复中明确说明跳过原因。

涉及后端代码或 schema 时，至少运行 `pytest backend\tests -q`。

涉及前端代码、组件、服务或路由时，至少运行受影响的服务测试与一次 `npm --prefix frontend run build`。

## 文档同步规则

新增或修改以下内容时必须同步更新对应文档：

| 变更类型 | 必须更新文档 |
|---|---|
| 数据字段、指标编码 | `docs/DATA_MODEL.md`、`docs/METRIC_DICTIONARY.md` |
| API 路径、请求或响应结构 | `docs/API.md` |
| 页面结构、路由 | `docs/FRONTEND_GUIDE.md`、`docs/USER_MANUAL.md` |
| 设计规范 | `docs/DESIGN_SYSTEM.md` |
| 模拟数据生成规则 | `docs/IMPORT_GUIDE.md`（保留文件名，内容是模拟场景指南）|
| 后端服务、依赖 | `docs/BACKEND_GUIDE.md` |
| 部署方式 | `docs/DEPLOYMENT.md` |
| 任意实际更新 | `docs/CHANGELOG.md`（每次必更）|

文档先于实现：架构、数据模型、API 契约和页面结构变更，先写或更新文档再写代码。

## Git commit 规则

- 仅在用户明确要求或本流程要求收尾时创建 commit，不擅自批量提交。
- 提交前用 `git status --short` 检查暂存范围，逐项确认没有：
  - 虚拟环境（`.venv/`、`venv/`、`env/`）；
  - Python / pytest 缓存；
  - `node_modules/`、`dist/`、`build/`；
  - 真实 Excel、GeoJSON、PDF、图片、SQLite 等数据文件；
  - `.env` 等敏感配置；
  - 与本次任务无关的修改。
- commit message 使用中文或英文均可，格式建议：
  - `feat: 新增 ...`
  - `fix: 修复 ...`
  - `docs: 更新 ...`
  - `refactor: 重构 ...`
  - `chore: ...`
- 每次提交至少包含一个对应的 `docs/CHANGELOG.md` 条目（除非纯 chore，如清理临时文件）。
- 不使用 `--amend` 修改已推送的提交，新改动追加新的 commit。
- 不使用 `--no-verify` 跳过 hook，除非用户明确要求。

## GitHub push 规则

- 只能 push 到 `claude/digital-twin-dev`。push 前确认本地分支与远端无冲突，使用 `git push -u origin claude/digital-twin-dev`（首次）或 `git push origin claude/digital-twin-dev`（后续）。
- 严禁直接 push 到 `main` 或 `codex/digital-twin-clean`。
- 严禁使用 `git push --force` 或 `--force-with-lease`，除非用户明确指示。
- push 前确认远端连通；如远端不可达，回复中说明并保留本地 commit。
- 完成阶段性功能后，由用户决定是否在 GitHub 上发起从 `claude/digital-twin-dev` 到 `codex/digital-twin-clean` 的 PR，Claude 不在未授权时主动创建 PR。

## Claude 最终回复格式

每次任务结束的最终回复必须包含以下内容（按顺序）：

1. **修改摘要**：1–3 句话说明这次做了什么。
2. **修改文件列表**：所有新增、修改、删除的文件路径。
3. **CHANGELOG 新增内容**：本次写入 `docs/CHANGELOG.md` 的条目摘要。
4. **是否运行测试**：列出运行的命令和结果。如果跳过了完整验证，明确说明原因。
5. **commit hash**：本次创建的 commit 短哈希；若未创建说明原因。
6. **push 结果**：是否推送、推送到哪个分支；若未推送说明原因。

如果是纯巡检或调研任务，没有任何文件改动，可以简化回复，但必须明确说明"未产生 commit""未推送"。
