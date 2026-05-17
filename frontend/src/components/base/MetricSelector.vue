<template>
  <a-select
    v-model:value="model"
    allow-clear
    :loading="loading"
    :disabled="disabled"
    :options="options"
    :placeholder="placeholder"
    show-search
    option-filter-prop="label"
  />
</template>

<script setup lang="ts">
import type { SelectProps } from 'ant-design-vue';

const model = defineModel<string | undefined>({ default: undefined });

withDefaults(
  defineProps<{
    options: SelectProps['options'];
    loading?: boolean;
    disabled?: boolean;
    placeholder?: string;
  }>(),
  {
    loading: false,
    disabled: false,
    placeholder: '选择指标',
  },
);
</script>
