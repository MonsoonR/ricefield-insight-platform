<template>
  <aside class="sticky top-0 flex h-screen w-[var(--rf-sidebar-width)] flex-col border-r border-[var(--rf-border-soft)] bg-[var(--rf-surface)] px-3.5 py-5">
    <RouterLink class="mb-3.5 flex items-center gap-3 border-b border-[var(--rf-border-soft)] px-1.5 pb-5 text-[var(--rf-text)] no-underline" to="/overview">
      <span class="grid size-10 shrink-0 place-items-center rounded-[10px] bg-gradient-to-br from-[var(--rf-primary)] to-[var(--rf-primary-darker)] text-white">
        <LandPlot class="size-[18px]" />
      </span>
      <span class="flex min-w-0 flex-col">
        <strong class="text-base font-bold leading-tight text-[var(--rf-text)]">稻田智研平台</strong>
        <small class="mt-1 text-[11px] leading-tight text-[var(--rf-text-soft)]">稻田数字孪生演示平台</small>
      </span>
    </RouterLink>

    <nav class="flex flex-1 flex-col gap-1">
      <RouterLink
        v-for="item in items"
        :key="item.path"
        class="group relative flex h-11 items-center gap-3 rounded-lg px-3 pl-[18px] text-sm font-semibold text-[var(--rf-text-muted)] no-underline transition hover:bg-[var(--rf-surface-soft)] hover:text-[var(--rf-text)] [&.router-link-active]:bg-[var(--rf-primary-soft)] [&.router-link-active]:font-bold [&.router-link-active]:text-[var(--rf-primary)]"
        :to="item.path"
      >
        <span class="absolute left-1 top-1/2 h-[22px] w-[3px] -translate-y-1/2 rounded-sm bg-transparent transition group-[.router-link-active]:bg-[var(--rf-primary)]" aria-hidden="true" />
        <component :is="item.icon" class="size-[17px] text-[var(--rf-text-soft)] transition group-hover:text-[var(--rf-text)] group-[.router-link-active]:text-[var(--rf-primary)]" />
        <span class="min-w-0 flex-1">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="border-t border-[var(--rf-border-soft)] pt-3.5 text-center">
      <small class="text-xs text-[var(--rf-text-soft)]">v1.0.0 · 演示场景</small>
    </div>
  </aside>
</template>

<script setup lang="ts">
import {
  BarChart3,
  BookOpen,
  Gauge,
  LandPlot,
  Map,
  TriangleAlert,
} from 'lucide-vue-next';
import { computed } from 'vue';

import { getTwinNavigationItems } from '@/services/pageLinkage';

const iconMap = {
  '/overview': Gauge,
  '/map-twin': Map,
  '/plot-detail': LandPlot,
  '/metric-compare': BarChart3,
  '/warnings': TriangleAlert,
  '/system-docs': BookOpen,
};

const items = computed(() =>
  getTwinNavigationItems().map((item) => ({
    ...item,
    icon: iconMap[item.path as keyof typeof iconMap],
  })),
);
</script>
