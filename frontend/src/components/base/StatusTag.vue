<template>
  <a-tag class="status-tag" :class="`status-tag--${config.tone}`">{{ config.label }}</a-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status?: string | null;
}>();

const config = computed(() => {
  switch (props.status) {
    case 'normal':
    case 'success':
      return { label: '正常', tone: 'normal' };
    case 'outlier':
    case 'abnormal':
      return { label: '预警', tone: 'warning' };
    case 'missing':
      return { label: '关注', tone: 'watch' };
    case 'error':
      return { label: '严重', tone: 'critical' };
    case 'no_data':
    case 'empty':
      return { label: '无数据', tone: 'empty' };
    default:
      return { label: props.status || '未知', tone: 'empty' };
  }
});
</script>

<style scoped>
.status-tag {
  margin-inline-end: 0;
  border: 0;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 9px;
}

.status-tag--normal {
  background: #e7f7ee;
  color: #087145;
}

.status-tag--watch {
  background: #fff4cf;
  color: #9a6700;
}

.status-tag--warning {
  background: #ffead5;
  color: #c2410c;
}

.status-tag--critical {
  background: #fee2dc;
  color: #c7281d;
}

.status-tag--empty {
  background: #eef2f1;
  color: #667789;
}
</style>
