<template>
  <aside class="app-sidebar">
    <RouterLink class="app-sidebar__brand" to="/overview">
      <span class="app-sidebar__logo">
        <ApartmentOutlined />
      </span>
      <span class="app-sidebar__brand-text">
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
        <span class="app-sidebar__indicator" aria-hidden="true" />
        <component :is="item.icon" class="app-sidebar__icon" />
        <span class="app-sidebar__label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="app-sidebar__footer">
      <small>v1.0.0 · 演示场景</small>
    </div>
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
  background: var(--rf-surface);
  padding: 22px 14px 18px;
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--rf-text);
  text-decoration: none;
  border-bottom: 1px solid var(--rf-border-soft);
  margin-bottom: 14px;
  padding: 0 6px 20px;
}

.app-sidebar__logo {
  display: grid;
  flex: 0 0 40px;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--rf-primary), var(--rf-primary-darker));
  color: #fff;
  font-size: 18px;
}

.app-sidebar__logo :deep(svg) {
  font-size: 18px;
}

.app-sidebar__brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-sidebar__brand-text strong {
  color: var(--rf-text);
  font-size: 16px;
  font-weight: 700;
  line-height: 1.2;
}

.app-sidebar__brand-text small {
  margin-top: 3px;
  color: var(--rf-text-soft);
  font-size: 11px;
  letter-spacing: 0.4px;
}

.app-sidebar__nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
}

.app-sidebar__link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  height: 44px;
  border-radius: 8px;
  color: var(--rf-text-muted);
  text-decoration: none;
  padding: 0 12px 0 18px;
  font-size: 14px;
  font-weight: 600;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.app-sidebar__indicator {
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 22px;
  border-radius: 2px;
  background: transparent;
  transition: background-color 0.15s ease;
}

.app-sidebar__icon {
  font-size: 17px;
  color: var(--rf-text-soft);
  transition: color 0.15s ease;
}

.app-sidebar__label {
  flex: 1;
  min-width: 0;
}

.app-sidebar__link:hover {
  background: var(--rf-surface-soft);
  color: var(--rf-text);
}

.app-sidebar__link:hover .app-sidebar__icon {
  color: var(--rf-text);
}

.app-sidebar__link.router-link-active {
  background: var(--rf-primary-soft);
  color: var(--rf-primary);
  font-weight: 700;
}

.app-sidebar__link.router-link-active .app-sidebar__icon {
  color: var(--rf-primary);
}

.app-sidebar__link.router-link-active .app-sidebar__indicator {
  background: var(--rf-primary);
}

.app-sidebar__footer {
  border-top: 1px solid var(--rf-border-soft);
  padding-top: 14px;
  text-align: center;
}

.app-sidebar__footer small {
  color: var(--rf-text-soft);
  font-size: 12px;
}
</style>
