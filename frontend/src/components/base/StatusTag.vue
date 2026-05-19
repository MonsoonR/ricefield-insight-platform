<template>
  <span class="status-tag" :class="`status-tag--${meta.level}`">{{ meta.label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { statusMetaFromQuality } from '@/utils/status';

const props = defineProps<{
  status?: string | null;
}>();

const meta = computed(() => statusMetaFromQuality(props.status));
</script>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 10px;
  line-height: 1.5;
  white-space: nowrap;
}

.status-tag--normal {
  background: var(--rf-status-normal-bg);
  color: var(--rf-status-normal);
}

.status-tag--watch {
  background: var(--rf-status-watch-bg);
  color: var(--rf-status-watch);
}

.status-tag--warning {
  background: var(--rf-status-warning-bg);
  color: var(--rf-status-warning);
}

.status-tag--critical {
  background: var(--rf-status-critical-bg);
  color: var(--rf-status-critical);
}

.status-tag--empty {
  background: var(--rf-status-empty-bg);
  color: var(--rf-status-empty);
}
</style>
