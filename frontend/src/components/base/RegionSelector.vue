<template>
  <div class="inline-flex min-h-10 rounded-[var(--rf-radius)] border border-[var(--rf-border-soft)] bg-white p-1 shadow-[var(--rf-shadow-xs)]">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="rounded-md px-3 py-1.5 text-sm font-semibold text-[var(--rf-text-muted)] transition hover:bg-[var(--rf-surface-soft)] disabled:cursor-not-allowed disabled:opacity-60"
      :class="{ 'bg-[var(--rf-primary-soft)] text-[var(--rf-primary)]': model === option.value }"
      :disabled="disabled"
      @click="model = option.value"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import type { RegionCode } from '@/types/api';

const model = defineModel<RegionCode>({ required: true });
withDefaults(defineProps<{ disabled?: boolean }>(), {
  disabled: false,
});

const options = [
  { label: '全部', value: 'all' },
  { label: '试验一区', value: 'east' },
  { label: '试验二区', value: 'west' },
] satisfies Array<{ label: string; value: RegionCode }>;
</script>
