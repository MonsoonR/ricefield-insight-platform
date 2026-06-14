<script setup lang="ts">
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

defineProps<{
  title?: string;
  description?: string;
}>();
</script>

<template>
  <Card class="rounded-md shadow-sm">
    <CardHeader
      v-if="title || description || $slots.actions"
      class="flex flex-row items-start justify-between gap-4 border-b border-border p-4"
    >
      <div class="min-w-0">
        <CardTitle v-if="title" class="truncate text-sm">{{ title }}</CardTitle>
        <CardDescription v-if="description" class="mt-1 text-xs">
          {{ description }}
        </CardDescription>
      </div>
      <div v-if="$slots.actions" class="flex shrink-0 items-center gap-2">
        <slot name="actions" />
      </div>
    </CardHeader>
    <CardContent class="p-4">
      <slot />
    </CardContent>
  </Card>
</template>
