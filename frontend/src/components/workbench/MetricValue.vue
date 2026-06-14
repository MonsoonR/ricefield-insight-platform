<script setup lang="ts">
import {
  Card,
  CardContent,
} from '@/components/ui/card';

defineProps<{
  label: string;
  value: string | number | null | undefined;
  unit?: string | null;
  note?: string;
}>();
</script>

<template>
  <Card class="rounded-md shadow-sm">
    <CardContent class="p-3">
      <div class="text-xs text-muted-foreground">{{ label }}</div>
      <div class="mt-1 flex items-baseline gap-1">
        <span class="text-xl font-semibold text-foreground">{{ value ?? '--' }}</span>
        <span v-if="unit" class="text-xs text-muted-foreground">{{ unit }}</span>
      </div>
      <div v-if="note" class="mt-1 truncate text-xs text-muted-foreground">{{ note }}</div>
    </CardContent>
  </Card>
</template>
