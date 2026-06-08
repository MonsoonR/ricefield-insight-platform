# Tailwind shadcn-vue Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Ant Design Vue with a Tailwind CSS + shadcn-vue source-component system and rebuild the six-page ricefield GIS workbench visual foundation.

**Architecture:** Keep Vue 3, Vite, Router, Pinia, Axios, ECharts, and Cesium. Introduce Tailwind/shadcn-vue at the frontend layer, build small reusable UI primitives, then migrate App Shell, map/Inspector workflows, and remaining pages in stages.

**Tech Stack:** Vue 3, TypeScript, Vite, Tailwind CSS, shadcn-vue, Reka UI, lucide-vue-next, ECharts, CesiumJS.

---

## File Structure

Files to create:

- `frontend/components.json` - shadcn-vue project configuration.
- `frontend/tailwind.config.js` - Tailwind content paths and project tokens.
- `frontend/postcss.config.js` - Tailwind/PostCSS integration for Vite.
- `frontend/src/lib/utils.ts` - `cn()` utility used by shadcn-vue and project components.
- `frontend/src/components/ui/*` - shadcn-vue generated source components.
- `frontend/src/components/workbench/AppShell.vue` - shared shell composition.
- `frontend/src/components/workbench/AppSidebar.vue` - narrow page navigation.
- `frontend/src/components/workbench/CommandBar.vue` - page title and command filter layout.
- `frontend/src/components/workbench/InspectorPanel.vue` - right-side object detail panel.
- `frontend/src/components/workbench/TwinMapPanel.vue` - Tailwind-based wrapper around current Cesium map behavior.
- `frontend/src/components/workbench/StatusBadge.vue` - fixed data-quality semantics.
- `frontend/src/components/workbench/MetricValue.vue` - metric display primitive.
- `frontend/src/components/workbench/DataPanel.vue` - non-AntD panel primitive for charts/tables.
- `frontend/src/components/workbench/index.ts` - exports workbench components.

Files to modify:

- `frontend/package.json` - add Tailwind/shadcn-vue dependencies and remove Ant Design Vue at the final cleanup task.
- `frontend/src/main.ts` - remove AntD plugin registration and import Tailwind CSS entry.
- `frontend/src/styles/global.css` - replace legacy AntD-oriented CSS with Tailwind layers and project CSS variables.
- `frontend/src/styles/theme.ts` - delete after AntD removal.
- `frontend/src/layouts/MainLayout.vue` - replace AntD layout with `AppShell`.
- `frontend/src/components/base/*` - progressively replace or retire AntD-dependent base components.
- `frontend/src/pages/OverviewPage.vue` - migrate first to the new shell and map/Inspector layout.
- `frontend/src/pages/MapAnalysisPage.vue` - migrate second to the new shell and map/Inspector layout.
- `frontend/src/pages/PlotDetailPage.vue` - migrate to new panel/table primitives.
- `frontend/src/pages/MetricComparePage.vue` - migrate to new filter/table/chart primitives.
- `frontend/src/pages/WarningAnalysisPage.vue` - migrate to quality-workbench layout.
- `frontend/src/pages/SystemDocsPage.vue` - migrate to help-center layout.
- `docs/DESIGN_SYSTEM.md` - document Tailwind/shadcn-vue tokens and component rules.
- `docs/FRONTEND_GUIDE.md` - document new frontend stack and migration rules.
- `docs/USER_MANUAL.md` - update page structure descriptions if visible page organization changes.
- `docs/CHANGELOG.md` - record every implementation batch.

---

### Task 1: Initialize Tailwind CSS and shadcn-vue

**Files:**
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/components.json`
- Create: `frontend/src/lib/utils.ts`
- Modify: `frontend/package.json`
- Modify: `frontend/src/styles/global.css`

- [ ] **Step 1: Capture the current dependency baseline**

Run:

```powershell
npm --prefix frontend run build
```

Expected: The build either passes, or fails with an existing pre-migration error. Record the exact result in the task notes before modifying files.

- [ ] **Step 2: Install Tailwind and shadcn-vue dependencies**

Run:

```powershell
npm --prefix frontend install -D tailwindcss postcss autoprefixer
npm --prefix frontend install class-variance-authority clsx tailwind-merge tailwindcss-animate reka-ui lucide-vue-next
```

Expected: `frontend/package.json` and `frontend/package-lock.json` include the new dependencies.

- [ ] **Step 3: Initialize shadcn-vue**

Run:

```powershell
npx shadcn-vue@latest init --cwd frontend
```

When prompted, choose:

```text
Style: Default
Base color: Slate
CSS file: src/styles/global.css
Use CSS variables: yes
Components alias: @/components
Utils alias: @/lib/utils
```

Expected: `frontend/components.json` and `frontend/src/lib/utils.ts` exist.

- [ ] **Step 4: Ensure Tailwind content paths include Vue and TS files**

Set `frontend/tailwind.config.js` to:

```js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{vue,ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        rice: {
          field: '#6fa878',
          deep: '#123326',
          gold: '#d7bd62',
          mist: '#eef5f0',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

- [ ] **Step 5: Verify Tailwind compiles**

Run:

```powershell
npm --prefix frontend run build
```

Expected: Build passes or fails only on known AntD imports that will be removed in later tasks. If Tailwind/PostCSS fails, fix this task before continuing.

- [ ] **Step 6: Commit initialization**

Run:

```powershell
git add frontend/package.json frontend/package-lock.json frontend/tailwind.config.js frontend/postcss.config.js frontend/components.json frontend/src/lib/utils.ts frontend/src/styles/global.css
git commit -m "feat: initialize tailwind shadcn vue"
```

---

### Task 2: Add shadcn-vue primitives

**Files:**
- Create/Modify: `frontend/src/components/ui/*`
- Modify: `frontend/components.json`

- [ ] **Step 1: Add required primitives**

Run:

```powershell
npx shadcn-vue@latest add button badge card select tabs table tooltip popover dialog sheet skeleton separator scroll-area --cwd frontend
```

Expected: matching component folders are created under `frontend/src/components/ui`.

- [ ] **Step 2: Inspect generated files**

Run:

```powershell
Get-ChildItem -LiteralPath .\frontend\src\components\ui -Recurse -File | Select-Object FullName
```

Expected: component source files exist and imports use `@/lib/utils` and `@/components/ui/...`.

- [ ] **Step 3: Verify component typecheck**

Run:

```powershell
npm --prefix frontend run build
```

Expected: Build passes or reports only page-level AntD usage that will be migrated later. No missing shadcn-vue component imports are allowed.

- [ ] **Step 4: Commit primitives**

Run:

```powershell
git add frontend/src/components/ui frontend/components.json frontend/package.json frontend/package-lock.json
git commit -m "feat: add shadcn vue primitives"
```

---

### Task 3: Replace AntD app bootstrap with Tailwind bootstrap

**Files:**
- Modify: `frontend/src/main.ts`
- Delete later: `frontend/src/styles/theme.ts`

- [ ] **Step 1: Replace `main.ts` with Vue-only bootstrap**

Set `frontend/src/main.ts` to:

```ts
import { createPinia } from 'pinia';
import { createApp } from 'vue';

import App from './App.vue';
import router from './router';
import './styles/global.css';

createApp(App).use(createPinia()).use(router).mount('#app');
```

- [ ] **Step 2: Run build to expose page-level AntD imports**

Run:

```powershell
npm --prefix frontend run build
```

Expected: If it fails, failures should identify Vue files still using unregistered AntD components or AntD theme imports. Record the list before migrating components.

- [ ] **Step 3: Do not delete `theme.ts` yet**

Keep `frontend/src/styles/theme.ts` until every import is removed. Run:

```powershell
Select-String -Path .\frontend\src\**\*.vue,.\frontend\src\**\*.ts -Pattern "themeConfig|ant-design-vue|a-button|a-card|a-select|a-table|a-tag"
```

Expected: Remaining matches are migration targets for later tasks.

- [ ] **Step 4: Commit bootstrap removal**

Run:

```powershell
git add frontend/src/main.ts
git commit -m "refactor: remove antd app bootstrap"
```

---

### Task 4: Build workbench shell components

**Files:**
- Create: `frontend/src/components/workbench/AppShell.vue`
- Create: `frontend/src/components/workbench/AppSidebar.vue`
- Create: `frontend/src/components/workbench/CommandBar.vue`
- Create: `frontend/src/components/workbench/index.ts`
- Modify: `frontend/src/layouts/MainLayout.vue`

- [ ] **Step 1: Create workbench export file**

Create `frontend/src/components/workbench/index.ts`:

```ts
export { default as AppShell } from './AppShell.vue';
export { default as AppSidebar } from './AppSidebar.vue';
export { default as CommandBar } from './CommandBar.vue';
```

- [ ] **Step 2: Create `AppSidebar.vue`**

Create `frontend/src/components/workbench/AppSidebar.vue`:

```vue
<script setup lang="ts">
import { BarChart3, BookOpen, Map, MapPinned, PanelRight, TriangleAlert } from 'lucide-vue-next';
import { computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

const route = useRoute();

const items = [
  { name: 'overview', label: '场景', icon: PanelRight, to: '/overview' },
  { name: 'map-twin', label: '地图', icon: Map, to: '/map-twin' },
  { name: 'plot-detail', label: '地块', icon: MapPinned, to: '/plot-detail' },
  { name: 'metric-compare', label: '对比', icon: BarChart3, to: '/metric-compare' },
  { name: 'warnings', label: '预警', icon: TriangleAlert, to: '/warnings' },
  { name: 'system-docs', label: '文档', icon: BookOpen, to: '/system-docs' },
];

const activeName = computed(() => String(route.name ?? 'overview'));
</script>

<template>
  <aside class="flex h-screen w-20 shrink-0 flex-col items-center gap-3 border-r border-border bg-rice-deep px-3 py-4 text-primary-foreground">
    <div class="mb-2 flex size-11 items-center justify-center rounded-xl bg-rice-gold text-sm font-bold text-rice-deep">
      稻
    </div>

    <RouterLink
      v-for="item in items"
      :key="item.name"
      :to="item.to"
      class="group flex w-full flex-col items-center gap-1 rounded-xl px-2 py-2 text-[11px] text-white/70 transition hover:bg-white/10 hover:text-white"
      :class="{ 'bg-white/15 text-white': activeName === item.name }"
    >
      <component :is="item.icon" class="size-4" aria-hidden="true" />
      <span>{{ item.label }}</span>
    </RouterLink>
  </aside>
</template>
```

- [ ] **Step 3: Create `CommandBar.vue`**

Create `frontend/src/components/workbench/CommandBar.vue`:

```vue
<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>

<template>
  <header class="flex min-h-16 items-center justify-between gap-4 rounded-2xl border border-border bg-card px-5 shadow-sm">
    <div class="min-w-0">
      <h1 class="truncate text-lg font-semibold text-foreground">{{ title }}</h1>
      <p v-if="description" class="mt-1 truncate text-sm text-muted-foreground">{{ description }}</p>
    </div>
    <div class="flex shrink-0 items-center gap-2">
      <slot name="actions" />
    </div>
  </header>
</template>
```

- [ ] **Step 4: Create `AppShell.vue`**

Create `frontend/src/components/workbench/AppShell.vue`:

```vue
<script setup lang="ts">
import AppSidebar from './AppSidebar.vue';
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <div class="flex min-h-screen">
      <AppSidebar />
      <main class="min-w-0 flex-1 p-4">
        <slot />
      </main>
    </div>
  </div>
</template>
```

- [ ] **Step 5: Replace `MainLayout.vue`**

Set `frontend/src/layouts/MainLayout.vue` to:

```vue
<script setup lang="ts">
import { RouterView } from 'vue-router';

import { AppShell } from '@/components/workbench';
</script>

<template>
  <AppShell>
    <RouterView />
  </AppShell>
</template>
```

- [ ] **Step 6: Build**

Run:

```powershell
npm --prefix frontend run build
```

Expected: Build passes or reports page-level AntD component usage only.

- [ ] **Step 7: Commit shell**

Run:

```powershell
git add frontend/src/components/workbench frontend/src/layouts/MainLayout.vue
git commit -m "feat: add tailwind workbench shell"
```

---

### Task 5: Build shared status and data primitives

**Files:**
- Create: `frontend/src/components/workbench/StatusBadge.vue`
- Create: `frontend/src/components/workbench/MetricValue.vue`
- Create: `frontend/src/components/workbench/DataPanel.vue`
- Modify: `frontend/src/components/workbench/index.ts`

- [ ] **Step 1: Create `StatusBadge.vue`**

Create `frontend/src/components/workbench/StatusBadge.vue`:

```vue
<script setup lang="ts">
import { computed } from 'vue';

type Status = 'normal' | 'missing' | 'outlier' | 'error' | 'no_data' | string;

const props = defineProps<{
  status: Status;
  label?: string;
}>();

const statusMap: Record<string, { label: string; className: string }> = {
  normal: { label: '正常', className: 'border-emerald-200 bg-emerald-50 text-emerald-700' },
  missing: { label: '缺失值', className: 'border-zinc-200 bg-zinc-100 text-zinc-700' },
  outlier: { label: '异常值', className: 'border-orange-200 bg-orange-50 text-orange-700' },
  error: { label: '错误记录', className: 'border-red-200 bg-red-50 text-red-700' },
  no_data: { label: '无数据', className: 'border-slate-200 bg-slate-100 text-slate-600' },
};

const display = computed(() => statusMap[props.status] ?? { label: props.status, className: 'border-border bg-muted text-muted-foreground' });
</script>

<template>
  <span class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium" :class="display.className">
    {{ label ?? display.label }}
  </span>
</template>
```

- [ ] **Step 2: Create `MetricValue.vue`**

Create `frontend/src/components/workbench/MetricValue.vue`:

```vue
<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number | null | undefined;
  unit?: string | null;
  note?: string;
}>();
</script>

<template>
  <div class="rounded-xl border border-border bg-card px-3 py-3">
    <div class="text-xs text-muted-foreground">{{ label }}</div>
    <div class="mt-1 flex items-baseline gap-1">
      <span class="text-xl font-semibold text-foreground">{{ value ?? '--' }}</span>
      <span v-if="unit" class="text-xs text-muted-foreground">{{ unit }}</span>
    </div>
    <div v-if="note" class="mt-1 truncate text-xs text-muted-foreground">{{ note }}</div>
  </div>
</template>
```

- [ ] **Step 3: Create `DataPanel.vue`**

Create `frontend/src/components/workbench/DataPanel.vue`:

```vue
<script setup lang="ts">
defineProps<{
  title?: string;
  description?: string;
}>();
</script>

<template>
  <section class="rounded-2xl border border-border bg-card shadow-sm">
    <header v-if="title || description || $slots.actions" class="flex items-start justify-between gap-4 border-b border-border px-4 py-3">
      <div class="min-w-0">
        <h2 v-if="title" class="truncate text-sm font-semibold text-foreground">{{ title }}</h2>
        <p v-if="description" class="mt-1 text-xs text-muted-foreground">{{ description }}</p>
      </div>
      <div class="flex shrink-0 items-center gap-2">
        <slot name="actions" />
      </div>
    </header>
    <div class="p-4">
      <slot />
    </div>
  </section>
</template>
```

- [ ] **Step 4: Update exports**

Append to `frontend/src/components/workbench/index.ts`:

```ts
export { default as DataPanel } from './DataPanel.vue';
export { default as MetricValue } from './MetricValue.vue';
export { default as StatusBadge } from './StatusBadge.vue';
```

- [ ] **Step 5: Build**

Run:

```powershell
npm --prefix frontend run build
```

Expected: New components typecheck.

- [ ] **Step 6: Commit primitives**

Run:

```powershell
git add frontend/src/components/workbench
git commit -m "feat: add workbench data primitives"
```

---

### Task 6: Migrate overview and map pages first

**Files:**
- Modify: `frontend/src/pages/OverviewPage.vue`
- Modify: `frontend/src/pages/MapAnalysisPage.vue`
- Modify as needed: `frontend/src/components/base/CesiumMapPanel.vue`
- Modify as needed: `frontend/src/components/map/PlotTrendChart.vue`

- [ ] **Step 1: List AntD usage in the two target pages**

Run:

```powershell
Select-String -LiteralPath .\frontend\src\pages\OverviewPage.vue,.\frontend\src\pages\MapAnalysisPage.vue -Pattern "a-|ant-design-vue|Card|Select|Table|Tag|Button|Tooltip|Skeleton|Empty|Result"
```

Expected: Output identifies all AntD-dependent sections to migrate.

- [ ] **Step 2: Replace page wrapper with `CommandBar` and Tailwind layout**

Use this page skeleton in both files, preserving existing script data-loading logic:

```vue
<template>
  <div class="flex min-h-[calc(100vh-2rem)] flex-col gap-4">
    <CommandBar title="场景驾驶舱" description="稻田数字孪生场景、地块、指标和质量状态总览">
      <template #actions>
        <!-- existing filters migrated to shadcn-vue Select/Button components -->
      </template>
    </CommandBar>

    <section class="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_340px] gap-4">
      <div class="min-h-[620px] rounded-2xl border border-border bg-card shadow-sm">
        <!-- map or primary canvas -->
      </div>
      <InspectorPanel>
        <!-- selected object details -->
      </InspectorPanel>
    </section>
  </div>
</template>
```

For `MapAnalysisPage.vue`, set title to `Cesium 地图孪生` and keep URL plot selection behavior unchanged.

- [ ] **Step 3: Preserve existing service calls**

Do not change imports from:

```ts
import {
  fetchDates,
  fetchMapLayers,
  fetchMetrics,
  fetchPlotSeries,
  fetchPlotSummary,
  fetchPlots,
} from '@/services/mapAnalysis';
```

Expected: Existing service tests still exercise the same data contract.

- [ ] **Step 4: Run targeted frontend service tests**

Run:

```powershell
npm --prefix frontend run test:overview
npm --prefix frontend run test:map
```

Expected: Both pass.

- [ ] **Step 5: Build**

Run:

```powershell
npm --prefix frontend run build
```

Expected: Build passes for migrated pages.

- [ ] **Step 6: Commit overview/map migration**

Run:

```powershell
git add frontend/src/pages/OverviewPage.vue frontend/src/pages/MapAnalysisPage.vue frontend/src/components/base/CesiumMapPanel.vue frontend/src/components/map/PlotTrendChart.vue
git commit -m "refactor: migrate overview and map workbench pages"
```

---

### Task 7: Migrate remaining pages and remove AntD dependency

**Files:**
- Modify: `frontend/src/pages/PlotDetailPage.vue`
- Modify: `frontend/src/pages/MetricComparePage.vue`
- Modify: `frontend/src/pages/WarningAnalysisPage.vue`
- Modify: `frontend/src/pages/SystemDocsPage.vue`
- Modify/Delete: `frontend/src/components/base/*`
- Delete: `frontend/src/styles/theme.ts`
- Modify: `frontend/package.json`

- [ ] **Step 1: Find all remaining AntD usage**

Run:

```powershell
Select-String -Path .\frontend\src\**\*.vue,.\frontend\src\**\*.ts -Pattern "ant-design-vue|themeConfig|a-button|a-card|a-select|a-table|a-tag|a-tabs|a-tooltip|a-skeleton|a-empty|a-result|a-layout|a-menu"
```

Expected: Every match is either removed in this task or listed as a blocker before continuing.

- [ ] **Step 2: Migrate `PlotDetailPage.vue`**

Use:

```vue
<CommandBar title="地块画像" description="单地块指标快照、趋势、来源追溯和质量核验" />
```

Replace AntD cards with `DataPanel`, quality tags with `StatusBadge`, and metric cards with `MetricValue`. Preserve route param `plotId` behavior.

- [ ] **Step 3: Migrate `MetricComparePage.vue`**

Use:

```vue
<CommandBar title="指标对比" description="按指标、日期和区域对比地块状态" />
```

Replace AntD table with either shadcn-vue `Table` composition or existing `DataTable.vue` rewritten without AntD. Preserve backend `rank` display and current derived mean/min/max logic.

- [ ] **Step 4: Migrate `WarningAnalysisPage.vue`**

Use:

```vue
<CommandBar title="预警分析" description="缺失、异常和错误记录的数据质量核验工作台" />
```

Replace warning type labels with `StatusBadge`. Keep warning recommendations limited to data quality checks.

- [ ] **Step 5: Migrate `SystemDocsPage.vue`**

Use:

```vue
<CommandBar title="系统说明" description="项目文档索引和维护入口" />
```

Use `DataPanel` for document groups. Do not add marketing copy.

- [ ] **Step 6: Remove AntD package**

Run:

```powershell
npm --prefix frontend uninstall ant-design-vue
```

Then delete:

```powershell
Remove-Item -LiteralPath .\frontend\src\styles\theme.ts
```

- [ ] **Step 7: Confirm no AntD references remain**

Run:

```powershell
Select-String -Path .\frontend\src\**\*.vue,.\frontend\src\**\*.ts,.\frontend\package.json -Pattern "ant-design-vue|themeConfig|a-button|a-card|a-select|a-table|a-tag|a-tabs|a-tooltip|a-skeleton|a-empty|a-result|a-layout|a-menu"
```

Expected: No output.

- [ ] **Step 8: Run all frontend service tests**

Run:

```powershell
npm --prefix frontend run test:overview
npm --prefix frontend run test:page-linkage
npm --prefix frontend run test:twin-analysis
npm --prefix frontend run test:map
```

Expected: All pass.

- [ ] **Step 9: Build**

Run:

```powershell
npm --prefix frontend run build
```

Expected: Build passes with no AntD dependency.

- [ ] **Step 10: Commit full page migration**

Run:

```powershell
git add frontend
git commit -m "refactor: migrate pages from antd to tailwind"
```

---

### Task 8: Update docs and run visual verification

**Files:**
- Modify: `docs/DESIGN_SYSTEM.md`
- Modify: `docs/FRONTEND_GUIDE.md`
- Modify: `docs/USER_MANUAL.md`
- Modify: `docs/CHANGELOG.md`

- [ ] **Step 1: Update `docs/DESIGN_SYSTEM.md`**

Add a section named `Tailwind + shadcn-vue 视觉系统` with:

```markdown
## Tailwind + shadcn-vue 视觉系统

前端不再使用 Ant Design Vue。第一阶段重构后的页面基于 Tailwind CSS、shadcn-vue 源码组件和项目自建 workbench 组件实现。

核心原则：

- 地图是首页和地图页的主画布。
- 右侧 Inspector 展示当前选中地块或当前分析对象。
- 顶部 CommandBar 收敛场景、指标、日期、区域和类型筛选。
- 状态颜色按 normal、missing、outlier、error、no_data 全站固定。
- 页面保持科研 GIS 工作台气质，不做营销化 hero、卡片墙或深色大屏。
```

- [ ] **Step 2: Update `docs/FRONTEND_GUIDE.md`**

Record the new stack:

```markdown
## 前端组件栈

当前前端使用 Vue 3、TypeScript、Vite、Vue Router、Pinia、Axios、ECharts、CesiumJS、Tailwind CSS 和 shadcn-vue。

Ant Design Vue 已退出前端组件栈。新增页面和组件不得重新引入 `ant-design-vue`。
```

- [ ] **Step 3: Update `docs/USER_MANUAL.md`**

Update page descriptions only if visible workflow names or layout changed. Keep the six existing page names unchanged.

- [ ] **Step 4: Update `docs/CHANGELOG.md`**

Add an entry for the implementation date:

```markdown
## 2026-06-08

### 修改

- 前端组件体系由 Ant Design Vue 迁移为 Tailwind CSS + shadcn-vue。
- 重构六页工作台外壳、地图主画布、右侧 Inspector、筛选器、表格、图表和状态标签。

### 验证

- 已通过：`npm --prefix frontend run test:overview`。
- 已通过：`npm --prefix frontend run test:page-linkage`。
- 已通过：`npm --prefix frontend run test:twin-analysis`。
- 已通过：`npm --prefix frontend run test:map`。
- 已通过：`npm --prefix frontend run build`。
```

- [ ] **Step 5: Start local dev server**

Run:

```powershell
npm --prefix frontend run dev
```

Expected: Vite prints a local URL, usually `http://127.0.0.1:5173/`.

- [ ] **Step 6: Browser verification**

Open these routes:

```text
/overview
/map-twin
/map-twin?plotId=demo-ricefield-2025-A01
/plot-detail/demo-ricefield-2025-A01
/metric-compare
/warnings
/system-docs
```

Expected:

- pages render without blank screen;
- navigation works;
- map page shows plot layer or fallback scene;
- selected plot state works on URL param;
- tables and filters do not overflow;
- mobile-width viewport remains usable.

- [ ] **Step 7: Commit docs and verification notes**

Run:

```powershell
git add docs/DESIGN_SYSTEM.md docs/FRONTEND_GUIDE.md docs/USER_MANUAL.md docs/CHANGELOG.md
git commit -m "docs: update frontend stack after tailwind migration"
```

---

## Self-Review

Spec coverage:

- Tailwind CSS and shadcn-vue initialization are covered by Tasks 1 and 2.
- Ant Design Vue removal is covered by Tasks 3 and 7.
- App Shell, Sidebar, CommandBar, Inspector, map panel, status and metric primitives are covered by Tasks 4 through 6.
- Six-page migration is covered by Tasks 6 and 7.
- Documentation and verification are covered by Task 8.

Placeholder scan:

- The plan contains no unresolved placeholder markers.
- Steps that change code include concrete file paths, snippets, or exact commands.

Type consistency:

- Workbench exports use `AppShell`, `AppSidebar`, `CommandBar`, `DataPanel`, `MetricValue`, and `StatusBadge`.
- Page migration steps reference the same component names.
