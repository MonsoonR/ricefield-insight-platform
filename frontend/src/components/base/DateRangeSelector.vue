<template>
  <div class="flex min-h-10 min-w-[250px] items-center gap-2 rounded-[var(--rf-radius)] border border-[var(--rf-border-soft)] bg-white px-3 py-1.5 shadow-[var(--rf-shadow-xs)]">
    <input
      v-model="startDate"
      type="date"
      class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[var(--rf-text)] outline-none"
      :disabled="disabled"
      aria-label="开始日期"
    />
    <span class="text-xs font-semibold text-[var(--rf-text-soft)]">至</span>
    <input
      v-model="endDate"
      type="date"
      class="min-w-0 flex-1 border-0 bg-transparent text-sm text-[var(--rf-text)] outline-none"
      :disabled="disabled"
      aria-label="结束日期"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const model = defineModel<[string, string] | undefined>({ default: undefined });

withDefaults(
  defineProps<{
    disabled?: boolean;
  }>(),
  {
    disabled: false,
  },
);

const startDate = computed({
  get: () => model.value?.[0] ?? '',
  set: (value: string) => updateRange(value, endDate.value),
});

const endDate = computed({
  get: () => model.value?.[1] ?? '',
  set: (value: string) => updateRange(startDate.value, value),
});

function updateRange(start: string, end: string) {
  model.value = start || end ? [start, end] : undefined;
}
</script>

