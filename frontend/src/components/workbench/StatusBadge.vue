<script setup lang="ts">
import { computed } from 'vue';

import { Badge } from '@/components/ui/badge';

type Status = 'normal' | 'missing' | 'outlier' | 'error' | 'no_data' | string;

const props = defineProps<{
  status: Status;
  label?: string;
}>();

const statusMap: Record<string, { label: string; className: string }> = {
  normal: { label: '正常', className: 'border-emerald-200 bg-emerald-50 text-emerald-700' },
  missing: { label: '缺失值', className: 'border-zinc-200 bg-zinc-100 text-zinc-700' },
  outlier: { label: '异常值', className: 'border-orange-200 bg-orange-50 text-orange-700' },
  error: { label: '错误记录', className: 'border-red-200 bg-red-50 text-red-700' },
  no_data: { label: '无数据', className: 'border-slate-200 bg-slate-100 text-slate-600' },
};

const display = computed(
  () =>
    statusMap[props.status] ?? {
      label: props.status,
      className: 'border-border bg-muted text-muted-foreground',
    },
);
</script>

<template>
  <Badge variant="outline" :class="display.className">
    {{ label ?? display.label }}
  </Badge>
</template>
