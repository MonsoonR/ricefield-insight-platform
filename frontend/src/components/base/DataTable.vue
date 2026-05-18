<template>
  <section class="data-table">
    <header v-if="title || $slots.extra" class="data-table__header">
      <div>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
      </div>
      <slot name="extra" />
    </header>
    <ErrorState v-if="error" :message="error" compact />
    <a-table
      v-else
      size="middle"
      :columns="columns"
      :data-source="dataSource"
      :loading="loading"
      :pagination="pagination"
      :row-key="rowKey"
      :scroll="scroll"
    >
      <template v-for="(_, name) in $slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData ?? {}" />
      </template>
      <template #emptyText>
        <EmptyState compact :description="emptyText" />
      </template>
    </a-table>
  </section>
</template>

<script setup lang="ts">
import type { TableColumnsType } from 'ant-design-vue';

import EmptyState from './EmptyState.vue';
import ErrorState from './ErrorState.vue';

withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    columns: TableColumnsType;
    dataSource: readonly object[];
    rowKey?: string | ((record: object) => string);
    loading?: boolean;
    error?: string;
    emptyText?: string;
    pagination?: false | Record<string, unknown>;
    scroll?: Record<string, string | number | true>;
  }>(),
  {
    title: '',
    description: '',
    rowKey: 'id',
    loading: false,
    error: '',
    emptyText: '暂无数据',
    pagination: false,
    scroll: undefined,
  },
);
</script>

<style scoped>
.data-table {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: var(--rf-surface);
  box-shadow: var(--rf-shadow-soft);
}

.data-table__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid rgba(237, 242, 239, 0.86);
  padding: 18px 20px 13px;
}

.data-table__header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
}

.data-table__header p {
  margin: 4px 0 0;
  color: var(--rf-text-muted);
  font-size: 12px;
}

.data-table :deep(.ant-table) {
  color: var(--rf-text);
  font-size: 13px;
}

.data-table :deep(.ant-table-thead > tr > th) {
  background: #f6f8f7;
  font-weight: 800;
}

.data-table :deep(.ant-table-tbody > tr > td) {
  border-color: var(--rf-border-soft);
}

.data-table :deep(.ant-pagination) {
  margin-right: 16px;
}
</style>
