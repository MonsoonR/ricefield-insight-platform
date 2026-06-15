<template>
  <header class="hidden h-[var(--rf-header-height)] items-center justify-between gap-6 border-b border-[var(--rf-border-soft)] bg-[var(--rf-surface)] px-7 lg:flex">
    <div class="min-w-0">
      <h1 class="m-0 text-xl font-bold leading-tight text-[var(--rf-text)]">{{ title }}</h1>
      <p v-if="subtitle" class="mt-1 text-[13px] leading-snug text-[var(--rf-text-muted)]">{{ subtitle }}</p>
    </div>
    <div class="flex items-center gap-4">
      <div class="inline-flex items-center gap-2 rounded-full border border-[var(--rf-border-soft)] bg-[var(--rf-surface-soft)] px-3.5 py-1.5" title="演示天气">
        <CloudSun class="size-4 text-[var(--rf-teal)]" />
        <span class="text-[13px] font-bold text-[var(--rf-text)]">26°C</span>
        <span class="hidden text-xs text-[var(--rf-text-muted)] xl:inline">晴 · 试验区</span>
      </div>
      <RouterLink class="relative inline-grid size-9 place-items-center rounded-md text-[var(--rf-text-muted)] transition hover:bg-[var(--rf-surface-soft)] hover:text-[var(--rf-text)]" to="/warnings" title="查看预警分析">
        <Bell class="size-[18px]" />
        <span
          v-if="alertCount > 0"
          class="absolute -right-1 -top-1 min-w-5 rounded-full bg-[var(--rf-warning)] px-1 text-center text-[11px] font-bold leading-5 text-white"
        >
          {{ alertCount > 99 ? '99+' : alertCount }}
        </span>
      </RouterLink>
      <RouterLink class="inline-grid size-9 place-items-center rounded-md text-[var(--rf-text-muted)] transition hover:bg-[var(--rf-surface-soft)] hover:text-[var(--rf-text)]" to="/system-docs" title="查看系统文档">
        <CircleHelp class="size-[18px]" />
      </RouterLink>
      <Separator orientation="vertical" class="h-6 bg-[var(--rf-border-soft)]" />
      <div class="flex items-center gap-2.5" title="当前角色">
        <span class="grid size-9 place-items-center rounded-full bg-[var(--rf-primary-soft)] text-[13px] font-bold text-[var(--rf-primary)]">研</span>
        <div class="hidden flex-col leading-tight xl:flex">
          <strong class="text-[13px] font-bold text-[var(--rf-text)]">演示用户</strong>
          <small class="text-[11px] text-[var(--rf-text-soft)]">研究员</small>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Bell, CircleHelp, CloudSun } from 'lucide-vue-next';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { fetchWarnings } from '@/api';
import { Separator } from '@/components/ui/separator';

const route = useRoute();
const alertCount = ref(0);

const title = computed(() => (route.meta?.title as string) ?? '稻田智研平台');
const subtitle = computed(() => (route.meta?.subtitle as string) ?? '');

onMounted(async () => {
  try {
    const response = await fetchWarnings();
    alertCount.value = response.total;
  } catch {
    alertCount.value = 0;
  }
});
</script>
