<template>
  <main class="page-container">
    <div class="page-container__heading">
      <div>
        <div v-if="breadcrumb" class="page-container__breadcrumb">{{ breadcrumb }}</div>
        <h1>{{ title }}</h1>
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
    title: string;
    description?: string;
    breadcrumb?: string;
  }>(),
  {
    description: '',
    breadcrumb: '',
  },
);
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-container__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 0 8px 2px;
}

.page-container__breadcrumb {
  margin-bottom: 8px;
  color: var(--rf-text-muted);
  font-size: 13px;
}

.page-container h1 {
  margin: 0;
  color: #0d1b2a;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.2;
}

.page-container p {
  margin: 7px 0 0;
  color: var(--rf-text-muted);
  font-size: 14px;
  line-height: 1.65;
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
