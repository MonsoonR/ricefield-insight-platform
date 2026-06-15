<template>
  <section class="filter-bar flex flex-wrap items-end gap-3 rounded-[var(--rf-radius-lg)] border border-[var(--rf-border-soft)] bg-[var(--rf-surface-soft)] p-4 shadow-[var(--rf-shadow-soft)]">
    <slot />
  </section>
</template>

<style scoped>
.filter-bar :deep(.filter-field) {
  display: flex;
  min-width: 176px;
  flex-direction: column;
  gap: 6px;
}

.filter-bar :deep(.filter-field > span:first-child) {
  color: var(--rf-text-muted);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
}

.filter-bar :deep(.filter-field--range) {
  min-width: 250px;
}

.filter-bar :deep(.filter-actions) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-height: var(--rf-control-height);
}

@media (max-width: 720px) {
  .filter-bar {
    align-items: stretch;
  }

  .filter-bar :deep(.filter-field),
  .filter-bar :deep(.filter-actions) {
    width: 100%;
  }
}
</style>
