<template>
  <span class="metric-value-tag" :class="`metric-value-tag--${tone}`">
    {{ displayValue }}
    <small v-if="unit">{{ unit }}</small>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

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

const tone = computed(() => {
  if (props.qualityFlag === 'outlier' || props.qualityFlag === 'error') {
    return 'red';
  }
  if (props.qualityFlag === 'missing') {
    return 'orange';
  }
  return 'green';
});
</script>

<style scoped>
.metric-value-tag {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  border-radius: 7px;
  font-weight: 850;
  padding: 3px 8px;
}

.metric-value-tag small {
  font-size: 11px;
  font-weight: 700;
}

.metric-value-tag--green {
  background: #e7f7ee;
  color: #04733a;
}

.metric-value-tag--orange {
  background: #fff7ed;
  color: #c2410c;
}

.metric-value-tag--red {
  background: #fef2f2;
  color: #dc2626;
}
</style>
