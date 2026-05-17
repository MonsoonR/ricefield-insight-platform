<template>
  <a-select
    v-model:value="model"
    allow-clear
    :loading="loading"
    :options="dateOptions"
    :placeholder="placeholder"
    show-search
    option-filter-prop="label"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue';

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
