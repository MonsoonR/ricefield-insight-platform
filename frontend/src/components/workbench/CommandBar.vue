<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>

<template>
  <header
    class="flex min-h-16 flex-col justify-center gap-3 rounded-md border border-border bg-card px-4 py-3 shadow-sm md:flex-row md:items-center md:justify-between md:px-5"
  >
    <div class="min-w-0">
      <h1 class="truncate text-lg font-semibold text-foreground">{{ title }}</h1>
      <p v-if="description" class="mt-1 truncate text-sm text-muted-foreground">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="flex w-full flex-wrap items-center gap-2 md:w-auto md:shrink-0 md:justify-end">
      <slot name="actions" />
    </div>
  </header>
</template>
