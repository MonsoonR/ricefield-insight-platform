<template>
  <aside class="app-sidebar">
    <RouterLink class="app-sidebar__brand" to="/overview">
      <span class="app-sidebar__logo">
        <ApartmentOutlined />
      </span>
      <span>
        <strong>稻田智研平台</strong>
        <small>稻田数字孪生演示平台</small>
      </span>
    </RouterLink>

    <nav class="app-sidebar__nav">
      <RouterLink
        v-for="item in items"
        :key="item.path"
        class="app-sidebar__link"
        :to="item.path"
      >
        <component :is="item.icon" />
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <button class="app-sidebar__collapse" type="button">收起菜单</button>
  </aside>
</template>

<script setup lang="ts">
import {
  ApartmentOutlined,
  BarChartOutlined,
  BookOutlined,
  DashboardOutlined,
  EnvironmentOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons-vue';
import { computed } from 'vue';

import { getTwinNavigationItems } from '@/services/pageLinkage';

const iconMap = {
  '/overview': DashboardOutlined,
  '/map-twin': EnvironmentOutlined,
  '/plot-detail': ApartmentOutlined,
  '/metric-compare': BarChartOutlined,
  '/warnings': ExclamationCircleOutlined,
  '/system-docs': BookOutlined,
};

const items = computed(() =>
  getTwinNavigationItems().map((item) => ({
    ...item,
    icon: iconMap[item.path as keyof typeof iconMap],
  })),
);
</script>

<style scoped>
.app-sidebar {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  width: var(--rf-sidebar-width);
  height: 100vh;
  border-right: 1px solid var(--rf-border-soft);
  background: rgba(255, 255, 255, 0.94);
  color: var(--rf-text);
  padding: 24px 18px 22px;
  box-shadow: 8px 0 28px rgba(15, 56, 37, 0.04);
  backdrop-filter: blur(16px);
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--rf-text);
  text-decoration: none;
  padding: 0 4px 28px;
}

.app-sidebar__logo {
  display: grid;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid rgba(21, 144, 93, 0.22);
  border-radius: 8px;
  background: linear-gradient(135deg, #e8f6ef, #ffffff);
  box-shadow: 0 10px 22px rgba(21, 144, 93, 0.12);
  color: var(--rf-primary);
  font-size: 22px;
}

.app-sidebar__brand strong,
.app-sidebar__brand small {
  display: block;
}

.app-sidebar__brand strong {
  font-size: 19px;
  font-weight: 900;
  line-height: 1.15;
}

.app-sidebar__brand small {
  margin-top: 2px;
  color: var(--rf-text-muted);
  font-size: 12px;
}

.app-sidebar__nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
}

.app-sidebar__link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 46px;
  border-radius: 8px;
  color: #435267;
  text-decoration: none;
  padding: 0 14px 0 16px;
  font-size: 14px;
  font-weight: 750;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.app-sidebar__link :deep(svg) {
  font-size: 18px;
}

.app-sidebar__link:hover,
.app-sidebar__link.router-link-active {
  background: linear-gradient(90deg, rgba(21, 144, 93, 0.14), rgba(21, 144, 93, 0.06));
  color: var(--rf-primary-dark);
  box-shadow: inset 3px 0 0 var(--rf-primary);
}

.app-sidebar__collapse {
  border: 0;
  background: transparent;
  color: var(--rf-text-muted);
  cursor: default;
  font-family: inherit;
  font-size: 13px;
  text-align: left;
  padding: 10px 4px 0;
}
</style>
