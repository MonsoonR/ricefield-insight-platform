<template>
  <div class="loading-state" :style="{ minHeight: `${height}px` }">
    <a-skeleton active :paragraph="{ rows }" />
  </div>
</template>

<script setup lang="ts">
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

<style scoped>
.loading-state {
  display: grid;
  align-items: center;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: var(--rf-surface);
  padding: 18px;
}
</style>
