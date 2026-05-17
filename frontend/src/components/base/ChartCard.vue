<template>
  <section class="chart-card">
    <header class="chart-card__header">
      <div>
        <h2>{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
      </div>
      <slot name="extra" />
    </header>
    <div class="chart-card__body">
      <LoadingState v-if="loading" :height="height" />
      <ErrorState v-else-if="error" :message="error" compact />
      <EmptyState v-else-if="empty" :description="emptyText" compact />
      <slot v-else />
    </div>
  </section>
</template>

<script setup lang="ts">
import EmptyState from './EmptyState.vue';
import ErrorState from './ErrorState.vue';
import LoadingState from './LoadingState.vue';

withDefaults(
  defineProps<{
    title: string;
    description?: string;
    loading?: boolean;
    error?: string;
    empty?: boolean;
    emptyText?: string;
    height?: number;
  }>(),
  {
    description: '',
    loading: false,
    error: '',
    empty: false,
    emptyText: '暂无可展示数据',
    height: 240,
  },
);
</script>

<style scoped>
.chart-card {
  min-width: 0;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: var(--rf-surface);
  box-shadow: var(--rf-shadow-soft);
}

.chart-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid var(--rf-border-soft);
  padding: 16px 18px 12px;
}

.chart-card__header h2 {
  margin: 0;
  color: var(--rf-text);
  font-size: 16px;
  font-weight: 800;
  line-height: 1.35;
}

.chart-card__header p {
  margin: 4px 0 0;
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.5;
}

.chart-card__body {
  min-width: 0;
  padding: 16px 18px;
}
</style>
