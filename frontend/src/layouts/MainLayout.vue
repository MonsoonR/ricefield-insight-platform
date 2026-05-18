<template>
  <div class="main-layout">
    <AppSidebar />
    <div class="main-layout__body">
      <AppHeader />
      <div class="main-layout__content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/base/AppHeader.vue';
import AppSidebar from '@/components/base/AppSidebar.vue';
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  background: var(--rf-bg);
}

.main-layout__body {
  min-width: 0;
  flex: 1;
}

.main-layout__content {
  min-height: calc(100vh - 66px);
  padding: 18px 26px 28px;
}

@media (max-width: 860px) {
  .main-layout {
    display: block;
  }

  .main-layout :deep(.app-sidebar) {
    position: static;
    width: 100%;
    height: auto;
  }

  .main-layout__content {
    padding: 18px 14px;
  }
}
</style>
