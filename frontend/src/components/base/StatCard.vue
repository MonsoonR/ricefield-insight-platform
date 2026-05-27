<template>
  <div class="stat-card" :class="`stat-card--${tone}`">
    <div class="stat-card__icon">
      <component :is="icon" v-if="icon" />
      <span v-else>{{ fallbackIcon }}</span>
    </div>
    <div class="stat-card__body">
      <span class="stat-card__label">{{ label }}</span>
      <strong>{{ value }}</strong>
      <small v-if="note">{{ note }}</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

withDefaults(
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
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 108px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: var(--rf-surface);
  box-shadow: var(--rf-shadow);
  padding: 18px 20px;
}

.stat-card__icon {
  display: grid;
  flex: 0 0 44px;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 50%;
  color: var(--tone);
  background: color-mix(in srgb, var(--tone) 12%, white);
  font-size: 18px;
}

.stat-card__icon :deep(svg) {
  font-size: 18px;
}

.stat-card__body {
  min-width: 0;
}

.stat-card__label,
.stat-card__body small {
  display: block;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.45;
}

.stat-card__body small {
  color: var(--rf-text-soft);
  font-size: 12px;
}

.stat-card__body strong {
  display: block;
  margin: 4px 0 4px;
  color: var(--rf-text);
  font-size: 28px;
  font-weight: 800;
  line-height: 1.1;
}

.stat-card--green {
  --tone: var(--rf-primary);
}

.stat-card--cyan {
  --tone: var(--rf-accent-cyan);
}

.stat-card--blue {
  --tone: var(--rf-info);
}

.stat-card--purple {
  --tone: var(--rf-purple);
}

.stat-card--yellow {
  --tone: var(--rf-status-watch);
}

.stat-card--orange {
  --tone: var(--rf-status-warning);
}

.stat-card--red {
  --tone: var(--rf-status-critical);
}
</style>
