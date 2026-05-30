<template>
  <main class="page-container">
    <div v-if="title || $slots.actions" class="page-container__heading">
      <div>
        <div v-if="breadcrumb" class="page-container__breadcrumb">{{ breadcrumb }}</div>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="page-container__actions">
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

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-container__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.page-container__breadcrumb {
  margin-bottom: 6px;
  color: var(--rf-text-soft);
  font-size: 12px;
}

.page-container h2 {
  margin: 0;
  color: var(--rf-text);
  font-size: 22px;
  font-weight: 700;
  line-height: 1.25;
}

.page-container p {
  margin: 6px 0 0;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.55;
  max-width: 760px;
}

.page-container__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 720px) {
  .page-container__heading {
    display: block;
  }

  .page-container__actions {
    justify-content: flex-start;
    margin-top: 12px;
  }
}
</style>
