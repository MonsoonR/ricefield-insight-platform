<template>
  <a-segmented v-model:value="model" :disabled="disabled" :options="options" />
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
];
</script>
