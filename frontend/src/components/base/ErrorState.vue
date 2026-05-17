<template>
  <div class="error-state" :class="{ 'error-state--compact': compact }">
    <div class="error-state__icon">!</div>
    <div>
      <strong>{{ title }}</strong>
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    message: string;
    compact?: boolean;
  }>(),
  {
    title: '数据加载失败',
    compact: false,
  },
);
</script>

<style scoped>
.error-state {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-height: 164px;
  border: 1px solid #fecaca;
  border-radius: var(--rf-radius);
  background: #fff5f5;
  padding: 16px;
}

.error-state--compact {
  min-height: 0;
}

.error-state__icon {
  display: grid;
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 50%;
  background: #fee2e2;
  color: var(--rf-error);
  font-weight: 900;
}

.error-state strong {
  display: block;
  color: #991b1b;
  font-size: 14px;
}

.error-state p {
  margin: 4px 0 0;
  color: #b91c1c;
  font-size: 13px;
  line-height: 1.6;
}
</style>
