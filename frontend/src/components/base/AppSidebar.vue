<template>
  <aside class="app-sidebar">
    <RouterLink class="app-sidebar__brand" to="/overview">
      <span class="app-sidebar__logo">稻</span>
      <span>
        <strong>稻田智研平台</strong>
        <small>RiceField Insight Platform</small>
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

    <div class="app-sidebar__card">
      <strong>专注稻田研究</strong>
      <span>数据驱动 · 科学决策</span>
      <div class="app-sidebar__plant">〽</div>
    </div>
    <small class="app-sidebar__version">v1.0.0</small>
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
  width: 240px;
  height: 100vh;
  padding: 24px 14px 22px;
  background:
    linear-gradient(165deg, rgba(3, 91, 54, 0.98), rgba(0, 48, 34, 1) 55%, rgba(0, 58, 38, 0.98)),
    #003823;
  color: #fff;
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
  text-decoration: none;
  padding: 0 8px 24px;
}

.app-sidebar__logo {
  display: grid;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 10px;
  background: linear-gradient(135deg, #57d37e, #07883f);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
  font-weight: 900;
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
  color: rgba(255, 255, 255, 0.72);
  font-size: 11px;
}

.app-sidebar__nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
}

.app-sidebar__link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.86);
  text-decoration: none;
  padding: 0 14px;
  font-size: 15px;
  font-weight: 700;
}

.app-sidebar__link :deep(svg) {
  font-size: 18px;
}

.app-sidebar__link:hover,
.app-sidebar__link.router-link-active {
  background: linear-gradient(135deg, #0c9a4d, #07883f);
  color: #fff;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
}

.app-sidebar__card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  background: rgba(8, 117, 69, 0.22);
  padding: 18px 16px;
}

.app-sidebar__card strong,
.app-sidebar__card span {
  display: block;
}

.app-sidebar__card span {
  margin-top: 6px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 12px;
}

.app-sidebar__plant {
  position: absolute;
  right: 14px;
  bottom: 4px;
  color: #facc15;
  font-size: 38px;
  opacity: 0.9;
}

.app-sidebar__version {
  display: block;
  margin-top: 18px;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}
</style>
