<template>
  <Badge
    variant="outline"
    class="rounded-full border-transparent px-2.5 py-0.5 text-xs font-bold"
    :style="badgeStyle"
  >
    {{ meta.label }}
  </Badge>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { Badge } from '@/components/ui/badge';
import { statusMetaFromQuality } from '@/utils/status';

const props = defineProps<{
  status?: string | null;
}>();

const meta = computed(() => statusMetaFromQuality(props.status));

const statusColors = {
  normal: ['var(--rf-success-soft)', 'var(--rf-success)'],
  watch: ['var(--rf-warning-soft)', 'var(--rf-warning)'],
  warning: ['var(--rf-warning-soft)', 'var(--rf-warning)'],
  critical: ['var(--rf-error-soft)', 'var(--rf-error)'],
  empty: ['var(--rf-bg-subtle)', 'var(--rf-text-muted)'],
};

const badgeStyle = computed(() => {
  const [background, color] = statusColors[meta.value.level];
  return { background, color };
});
</script>
