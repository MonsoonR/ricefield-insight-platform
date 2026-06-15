<template>
  <Badge
    variant="outline"
    class="rounded-full px-2.5 py-0.5 text-xs font-bold"
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

const badgeStyle = computed(() => {
  return {
    background: meta.value.background,
    borderColor: meta.value.border,
    color: meta.value.color,
  };
});
</script>
