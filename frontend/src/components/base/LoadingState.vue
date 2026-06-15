<template>
  <div
    class="grid gap-3 rounded-[var(--rf-radius-lg)] border border-[var(--rf-border-soft)] bg-[var(--rf-surface)] p-[18px]"
    :style="{ minHeight: `${height}px` }"
  >
    <Skeleton class="h-4 w-2/5" />
    <Skeleton
      v-for="row in rows"
      :key="row"
      class="h-4 w-full"
      :class="{ 'w-4/5': row === rows }"
    />
  </div>
</template>

<script setup lang="ts">
import { Skeleton } from '@/components/ui/skeleton';

withDefaults(
  defineProps<{
    height?: number;
    rows?: number;
  }>(),
  {
    height: 180,
    rows: 4,
  },
);
</script>
