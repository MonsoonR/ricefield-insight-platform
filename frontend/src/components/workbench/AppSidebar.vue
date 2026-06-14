<script setup lang="ts">
import {
  BarChart3,
  BookOpen,
  Map,
  MapPinned,
  PanelRight,
  TriangleAlert,
} from 'lucide-vue-next';
import { computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

const route = useRoute();

const items = [
  { name: 'overview', label: '场景', icon: PanelRight, to: '/overview' },
  { name: 'map-twin', label: '地图', icon: Map, to: '/map-twin' },
  { name: 'plot-detail', label: '地块', icon: MapPinned, to: '/plot-detail/demo-ricefield-2025-A01' },
  { name: 'metric-compare', label: '对比', icon: BarChart3, to: '/metric-compare' },
  { name: 'warnings', label: '预警', icon: TriangleAlert, to: '/warnings' },
  { name: 'system-docs', label: '文档', icon: BookOpen, to: '/system-docs' },
];

const activeName = computed(() => String(route.name ?? 'overview'));
</script>

<template>
  <aside
    class="flex shrink-0 flex-row items-center gap-2 border-b border-border bg-rice-deep px-3 py-2 text-primary-foreground md:h-screen md:w-20 md:flex-col md:border-b-0 md:border-r md:py-4"
  >
    <div
      class="flex size-10 shrink-0 items-center justify-center rounded-md bg-rice-gold text-sm font-bold text-rice-deep md:mb-2 md:size-11"
    >
      稻
    </div>

    <nav class="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto md:flex-col md:overflow-visible">
      <RouterLink
        v-for="item in items"
        :key="item.name"
        :to="item.to"
        class="group flex min-w-14 flex-col items-center gap-1 rounded-md px-2 py-2 text-[11px] text-white/70 transition hover:bg-white/10 hover:text-white md:w-full"
        :class="{ 'bg-white/15 text-white': activeName === item.name }"
      >
        <component :is="item.icon" aria-hidden="true" />
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>
