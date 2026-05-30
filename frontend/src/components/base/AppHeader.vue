<template>
  <header class="app-header">
    <div class="app-header__title">
      <h1>{{ title }}</h1>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    <div class="app-header__actions">
      <div class="app-header__weather" title="演示天气">
        <CloudOutlined class="app-header__weather-icon" />
        <span class="app-header__weather-temp">26°C</span>
        <span class="app-header__weather-text">晴 · 试验区</span>
      </div>
      <RouterLink class="app-header__icon-link" to="/warnings" title="查看预警分析">
        <a-badge
          :count="alertCount"
          :offset="[-2, 2]"
          :number-style="{ background: 'var(--rf-status-warning)', boxShadow: 'none' }"
        >
          <BellOutlined class="app-header__icon" />
        </a-badge>
      </RouterLink>
      <RouterLink class="app-header__icon-link" to="/system-docs" title="查看系统文档">
        <QuestionCircleOutlined class="app-header__icon" />
      </RouterLink>
      <a-divider type="vertical" class="app-header__divider" />
      <div class="app-header__user" title="当前角色">
        <span class="app-header__avatar">研</span>
        <div class="app-header__user-text">
          <strong>演示用户</strong>
          <small>研究员</small>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import {
  BellOutlined,
  CloudOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

import { fetchWarnings } from '@/api';

const route = useRoute();
const alertCount = ref(0);

const title = computed(() => (route.meta?.title as string) ?? '稻田智研平台');
const subtitle = computed(() => (route.meta?.subtitle as string) ?? '');

onMounted(async () => {
  try {
    const response = await fetchWarnings();
    alertCount.value = response.total;
  } catch {
    alertCount.value = 0;
  }
});
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  height: var(--rf-header-height);
  border-bottom: 1px solid var(--rf-border-soft);
  background: var(--rf-surface);
  padding: 0 28px;
}

.app-header__title {
  min-width: 0;
}

.app-header__title h1 {
  margin: 0;
  color: var(--rf-text);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.app-header__title p {
  margin: 3px 0 0;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.4;
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.app-header__weather {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 999px;
  background: var(--rf-surface-soft);
  padding: 6px 14px;
}

.app-header__weather-icon {
  color: var(--rf-accent-cyan);
  font-size: 16px;
}

.app-header__weather-temp {
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.app-header__weather-text {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.app-header__icon-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: var(--rf-text-muted);
  transition: background 0.15s ease, color 0.15s ease;
}

.app-header__icon-link:hover {
  background: var(--rf-surface-soft);
  color: var(--rf-text);
}

.app-header__icon {
  font-size: 18px;
}

.app-header__divider {
  height: 22px;
  margin: 0 2px;
  background: var(--rf-border-soft);
}

.app-header__user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-header__avatar {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 50%;
  background: var(--rf-primary-soft);
  color: var(--rf-primary);
  font-size: 13px;
  font-weight: 700;
}

.app-header__user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.app-header__user-text strong {
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.app-header__user-text small {
  color: var(--rf-text-soft);
  font-size: 11px;
}

@media (max-width: 1180px) {
  .app-header__weather-text {
    display: none;
  }
  .app-header__user-text {
    display: none;
  }
}

@media (max-width: 860px) {
  .app-header {
    display: none;
  }
}
</style>
