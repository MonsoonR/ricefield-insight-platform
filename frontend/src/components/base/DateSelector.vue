<template>
  <SelectControl
    v-model="model"
    :loading="loading"
    :options="dateOptions"
    :placeholder="placeholder"
    empty-label="不限日期"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';

import SelectControl from './SelectControl.vue';

const model = defineModel<string | undefined>({ default: undefined });

const props = withDefaults(
  defineProps<{
    dates: string[];
    loading?: boolean;
    placeholder?: string;
  }>(),
  {
    loading: false,
    placeholder: '选择日期',
  },
);

const dateOptions = computed(() =>
  props.dates.map((date) => ({
    label: date,
    value: date,
  })),
);
</script>
