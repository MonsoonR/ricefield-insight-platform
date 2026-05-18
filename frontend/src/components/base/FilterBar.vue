<template>
  <section class="filter-bar">
    <slot />
  </section>
</template>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: var(--rf-shadow-soft);
  padding: 16px 18px;
}

.filter-bar :deep(.ant-form-item) {
  margin-bottom: 0;
}

.filter-bar :deep(.ant-select),
.filter-bar :deep(.ant-picker),
.filter-bar :deep(.ant-input-affix-wrapper) {
  min-width: 176px;
}
</style>
