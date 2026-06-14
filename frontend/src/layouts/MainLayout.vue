<script setup lang="ts">
import { RouterView } from 'vue-router';

import { AppShell } from '@/components/workbench';
</script>

<template>
  <AppShell>
    <RouterView />
  </AppShell>
</template>
