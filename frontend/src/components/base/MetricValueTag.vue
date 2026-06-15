<template>
  <span
    class="inline-flex items-baseline gap-1 rounded-md px-2 py-1 text-[13px] font-bold"
    :style="tagStyle"
  >
    {{ displayValue }}
    <small v-if="unit" class="text-[11px] font-semibold opacity-85">{{ unit }}</small>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { mapQualityToStatus } from '@/utils/status';

const props = withDefaults(
  defineProps<{
    value?: number | string | null;
    unit?: string | null;
    qualityFlag?: string | null;
  }>(),
  {
    value: null,
    unit: '',
    qualityFlag: 'normal',
  },
);

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') {
    return '--';
  }
  return typeof props.value === 'number' ? props.value.toLocaleString('zh-CN') : props.value;
});

const level = computed(() => mapQualityToStatus(props.qualityFlag));

const statusColors = {
  normal: ['var(--rf-success-soft)', 'var(--rf-success)'],
  watch: ['var(--rf-warning-soft)', 'var(--rf-warning)'],
  warning: ['var(--rf-warning-soft)', 'var(--rf-warning)'],
  critical: ['var(--rf-error-soft)', 'var(--rf-error)'],
  empty: ['var(--rf-bg-subtle)', 'var(--rf-text-muted)'],
};

const tagStyle = computed(() => {
  const [background, color] = statusColors[level.value];
  return { background, color };
});
</script>
