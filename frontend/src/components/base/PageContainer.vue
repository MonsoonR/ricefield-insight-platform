<template>
  <main class="flex flex-col gap-5">
    <div v-if="title || $slots.actions" class="flex items-start justify-between gap-[18px] max-md:block">
      <div class="min-w-0">
        <div v-if="breadcrumb" class="mb-1.5 text-xs text-[var(--rf-text-soft)]">{{ breadcrumb }}</div>
        <h2 v-if="title" class="m-0 text-[22px] font-bold leading-tight text-[var(--rf-text)]">{{ title }}</h2>
        <p v-if="description" class="mt-1.5 max-w-[760px] text-[13px] leading-relaxed text-[var(--rf-text-muted)]">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="flex flex-wrap justify-end gap-2.5 max-md:mt-3 max-md:justify-start">
        <slot name="actions" />
      </div>
    </div>
    <slot />
  </main>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description?: string;
    breadcrumb?: string;
  }>(),
  {
    title: '',
    description: '',
    breadcrumb: '',
  },
);
</script>
