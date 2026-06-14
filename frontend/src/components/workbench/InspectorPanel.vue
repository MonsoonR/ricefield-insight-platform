<script setup lang="ts">
defineProps<{
  title?: string;
  description?: string;
}>();
</script>

<template>
  <aside class="min-w-0 rounded-md border border-border bg-card shadow-sm">
    <header
      v-if="title || description || $slots.actions"
      class="flex items-start justify-between gap-4 border-b border-border p-4"
    >
      <div class="min-w-0">
        <h2 v-if="title" class="truncate text-sm font-semibold text-foreground">{{ title }}</h2>
        <p v-if="description" class="mt-1 text-xs text-muted-foreground">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="flex shrink-0 items-center gap-2">
        <slot name="actions" />
      </div>
    </header>
    <div class="p-4">
      <slot />
    </div>
  </aside>
</template>
