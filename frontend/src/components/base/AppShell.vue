<template>
  <div class="min-h-screen bg-[var(--rf-bg)] text-[var(--rf-text)]">
    <div class="flex min-h-screen">
      <AppSidebar class="hidden lg:flex" />
      <div class="flex min-w-0 flex-1 flex-col">
        <AppHeader />
        <main class="min-w-0 flex-1 p-3 md:p-4">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue';
import AppSidebar from './AppSidebar.vue';
</script>
