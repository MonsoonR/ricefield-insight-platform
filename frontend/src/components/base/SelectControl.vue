<template>
  <Select :model-value="internalValue" :disabled="disabled || loading" @update:model-value="handleUpdate">
    <SelectTrigger class="min-h-10 min-w-[176px] rounded-[var(--rf-radius)] border-[var(--rf-border-soft)] bg-white shadow-[var(--rf-shadow-xs)]">
      <SelectValue :placeholder="loading ? '加载中...' : placeholder" />
    </SelectTrigger>
    <SelectContent>
      <SelectGroup>
        <SelectItem v-if="allowEmpty" :value="EMPTY_VALUE">
          {{ emptyLabel }}
        </SelectItem>
        <SelectItem
          v-for="option in normalizedOptions"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface SelectControlOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

const EMPTY_VALUE = '__rf_empty__';

const model = defineModel<string | undefined>({ default: undefined });

const props = withDefaults(
  defineProps<{
    options: SelectControlOption[];
    loading?: boolean;
    disabled?: boolean;
    placeholder?: string;
    allowEmpty?: boolean;
    emptyLabel?: string;
  }>(),
  {
    loading: false,
    disabled: false,
    placeholder: '请选择',
    allowEmpty: true,
    emptyLabel: '全部',
  },
);

const normalizedOptions = computed(() =>
  props.options
    .filter((option) => option.value !== '' && option.value !== EMPTY_VALUE)
    .map((option) => ({
      ...option,
      value: String(option.value),
    })),
);

const internalValue = computed(() =>
  model.value === undefined || model.value === '' ? EMPTY_VALUE : String(model.value),
);

function handleUpdate(value: unknown) {
  const rawValue = Array.isArray(value) ? value[0] : value;
  const nextValue = rawValue === null || rawValue === undefined ? EMPTY_VALUE : String(rawValue);
  model.value = nextValue === EMPTY_VALUE ? undefined : nextValue;
}
</script>
