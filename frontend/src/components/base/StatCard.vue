<template>
  <div
    class="flex min-h-[108px] items-center gap-4 rounded-[var(--rf-radius-lg)] border border-[var(--rf-border-soft)] bg-[var(--rf-surface)] p-5 shadow-[var(--rf-shadow)]"
    :style="toneStyle"
  >
    <div class="grid size-11 shrink-0 place-items-center rounded-full text-[var(--tone)] [background:color-mix(in_srgb,var(--tone)_12%,white)]">
      <component :is="icon" v-if="icon" />
      <span v-else>{{ fallbackIcon }}</span>
    </div>
    <div class="min-w-0">
      <span class="block text-[13px] leading-snug text-[var(--rf-text-muted)]">{{ label }}</span>
      <strong class="my-1 block text-[28px] font-extrabold leading-none text-[var(--rf-text)]">{{ value }}</strong>
      <small v-if="note" class="block text-xs leading-snug text-[var(--rf-text-soft)]">{{ note }}</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Component } from 'vue';

const props = withDefaults(
  defineProps<{
    label: string;
    value: string | number;
    note?: string;
    tone?: 'green' | 'blue' | 'purple' | 'orange' | 'red' | 'cyan' | 'yellow';
    icon?: Component;
    fallbackIcon?: string;
  }>(),
  {
    note: '',
    tone: 'green',
    icon: undefined,
    fallbackIcon: '●',
  },
);

const toneMap = {
  green: 'var(--rf-primary)',
  cyan: 'var(--rf-teal)',
  blue: 'var(--rf-info)',
  purple: 'var(--rf-purple)',
  yellow: 'var(--rf-warning)',
  orange: 'var(--rf-warning)',
  red: 'var(--rf-error)',
};

const toneStyle = computed(() => ({
  '--tone': toneMap[props.tone],
}));
</script>
