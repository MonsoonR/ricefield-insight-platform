<template>
  <div class="empty-state" :class="{ 'empty-state--compact': compact }">
    <a-empty :description="description" />
  </div>
</template>

<script setup lang="ts">
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

<style scoped>
.empty-state {
  display: grid;
  min-height: 220px;
  place-items: center;
  color: var(--rf-text-muted);
}

.empty-state--compact {
  min-height: 118px;
}
</style>
