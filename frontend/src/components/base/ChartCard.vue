<template>
  <section class="min-w-0 rounded-[var(--rf-radius-lg)] border border-[var(--rf-border-soft)] bg-[var(--rf-surface)] shadow-[var(--rf-shadow)]">
    <header class="flex items-start justify-between gap-3.5 border-b border-[var(--rf-border-soft)] px-5 py-4">
      <div>
        <h2 class="m-0 text-base font-bold leading-tight text-[var(--rf-text)]">{{ title }}</h2>
        <p v-if="description" class="mt-1 text-xs leading-normal text-[var(--rf-text-muted)]">{{ description }}</p>
      </div>
      <slot name="extra" />
    </header>
    <div class="min-w-0 px-5 py-4">
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
