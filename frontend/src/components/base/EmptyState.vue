<template>
  <div
    class="grid place-items-center text-center text-[var(--rf-text-muted)]"
    :class="compact ? 'min-h-[118px]' : 'min-h-[220px]'"
  >
    <div class="grid justify-items-center gap-2">
      <Inbox class="size-9 text-[var(--rf-text-soft)]" />
      <span class="text-sm font-semibold">{{ description }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Inbox } from 'lucide-vue-next';

withDefaults(
  defineProps<{
    description?: string;
    compact?: boolean;
  }>(),
  {
    description: '暂无数据',
    compact: false,
  },
);
</script>
