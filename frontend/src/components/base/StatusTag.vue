<template>
  <a-tag class="status-tag" :color="config.color">{{ config.label }}</a-tag>
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
      return { label: '有效数据', color: 'success' };
    case 'outlier':
    case 'abnormal':
      return { label: '异常', color: 'error' };
    case 'missing':
      return { label: '缺失', color: 'warning' };
    case 'error':
      return { label: '错误', color: 'red' };
    case 'no_data':
    case 'empty':
      return { label: '无数据', color: 'default' };
    default:
      return { label: props.status || '未知', color: 'default' };
  }
});
</script>

<style scoped>
.status-tag {
  margin-inline-end: 0;
  border-radius: 999px;
  font-weight: 700;
}
</style>
