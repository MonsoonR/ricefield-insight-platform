<template>
  <SelectControl
    v-model="model"
    :loading="loading"
    :disabled="disabled"
    :options="options"
    :placeholder="placeholder"
    empty-label="全部指标"
  />
</template>

<script setup lang="ts">
import SelectControl, { type SelectControlOption } from './SelectControl.vue';

const model = defineModel<string | undefined>({ default: undefined });

withDefaults(
  defineProps<{
    options: SelectControlOption[];
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
