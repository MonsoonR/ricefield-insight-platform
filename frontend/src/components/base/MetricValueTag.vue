<template>
  <span class="metric-value-tag" :class="`metric-value-tag--${level}`">
    {{ displayValue }}
    <small v-if="unit">{{ unit }}</small>
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
</script>

<style scoped>
.metric-value-tag {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  border-radius: 6px;
  font-weight: 700;
  padding: 3px 8px;
  font-size: 13px;
}

.metric-value-tag small {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.85;
}

.metric-value-tag--normal {
  background: var(--rf-status-normal-bg);
  color: var(--rf-status-normal);
}

.metric-value-tag--watch {
  background: var(--rf-status-watch-bg);
  color: var(--rf-status-watch);
}

.metric-value-tag--warning {
  background: var(--rf-status-warning-bg);
  color: var(--rf-status-warning);
}

.metric-value-tag--critical {
  background: var(--rf-status-critical-bg);
  color: var(--rf-status-critical);
}

.metric-value-tag--empty {
  background: var(--rf-status-empty-bg);
  color: var(--rf-status-empty);
}
</style>
