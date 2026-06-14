<script setup lang="ts">
import AppSidebar from './AppSidebar.vue';
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <div class="flex min-h-screen flex-col md:flex-row">
      <AppSidebar />
      <main class="min-w-0 flex-1 p-3 md:p-4">
        <slot />
      </main>
    </div>
  </div>
</template>
