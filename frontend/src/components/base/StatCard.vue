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
    tone?: 'green' | 'blue' | 'purple' | 'orange' | 'red' | 'cyan';
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
  min-height: 112px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.84)),
    var(--rf-surface);
  box-shadow: var(--rf-shadow-soft);
  padding: 20px 22px;
}

.stat-card__icon {
  display: grid;
  flex: 0 0 54px;
  width: 54px;
  height: 54px;
  place-items: center;
  border-radius: 50%;
  color: var(--tone);
  background: color-mix(in srgb, var(--tone) 13%, white);
  font-size: 24px;
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

.stat-card__body strong {
  display: block;
  margin: 5px 0 4px;
  color: var(--rf-text);
  font-size: 28px;
  font-weight: 850;
  line-height: 1.1;
}

.stat-card--green {
  --tone: var(--rf-primary);
}

.stat-card--blue {
  --tone: var(--rf-info);
}

.stat-card--purple {
  --tone: var(--rf-purple);
}

.stat-card--orange {
  --tone: var(--rf-warning);
}

.stat-card--red {
  --tone: var(--rf-error);
}

.stat-card--cyan {
  --tone: var(--rf-cyan);
}
</style>
