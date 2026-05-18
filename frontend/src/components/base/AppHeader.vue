<template>
  <header class="app-header">
    <div class="app-header__context" aria-label="全局数据状态">
      <span>{{ selectedScenarioName }}</span>
      <strong>{{ selectedDate || '最新观测日期' }}</strong>
      <small>{{ selectedMetricName }}</small>
    </div>
    <div class="app-header__actions">
      <span class="app-header__weather">26°C</span>
      <RouterLink class="app-header__icon-link" to="/warnings" title="查看预警分析">
        <a-badge :count="alertCount" size="small">
          <BellOutlined class="app-header__icon" />
        </a-badge>
      </RouterLink>
      <RouterLink class="app-header__icon-link" to="/system-docs" title="查看系统文档">
        <QuestionCircleOutlined class="app-header__icon" />
      </RouterLink>
      <div class="app-header__user" title="当前角色">
        <span>研</span>
        <strong>Demo User</strong>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import {
  BellOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue';
import { computed, onMounted, ref } from 'vue';

import { fetchCurrentScenario, fetchDates, fetchMetrics, fetchWarnings } from '@/api';

const selectedScenarioName = ref<string>('稻田数字孪生演示场景');
const selectedDate = ref<string>();
const selectedMetricName = ref<string>('标准化模拟数据');
const alertCount = ref(0);

const dates = ref<string[]>([]);

const latestDate = computed(() => dates.value[dates.value.length - 1]);

onMounted(async () => {
  const [scenarioResponse, datesResponse, metricsResponse, warningsResponse] = await Promise.allSettled([
    fetchCurrentScenario(),
    fetchDates(),
    fetchMetrics(),
    fetchWarnings(),
  ]);

  if (scenarioResponse.status === 'fulfilled') {
    selectedScenarioName.value = scenarioResponse.value.scenario_name;
  }
  if (datesResponse.status === 'fulfilled') {
    dates.value = datesResponse.value.items;
    selectedDate.value = latestDate.value;
  }
  if (metricsResponse.status === 'fulfilled') {
    selectedMetricName.value = `${metricsResponse.value.items.length} 个指标在线`;
  }
  if (warningsResponse.status === 'fulfilled') {
    alertCount.value = warningsResponse.value.total;
  }
});
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  min-height: 66px;
  background: transparent;
  padding: 0 26px;
}

.app-header__context {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  color: var(--rf-text-muted);
  font-size: 13px;
}

.app-header__context span {
  color: var(--rf-text);
  font-weight: 850;
}

.app-header__context strong {
  font-weight: 800;
}

.app-header__context small {
  color: var(--rf-primary);
  font-weight: 800;
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-header__weather {
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 850;
}

.app-header__icon-link {
  display: inline-flex;
  color: inherit;
}

.app-header__icon {
  color: #102033;
  font-size: 20px;
}

.app-header__user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-header__user span {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 50%;
  background: var(--rf-primary);
  color: #fff;
  font-weight: 900;
}

.app-header__user strong {
  white-space: nowrap;
  font-size: 14px;
}

@media (max-width: 1180px) {
  .app-header__context small,
  .app-header__context strong {
    display: none;
  }
}

@media (max-width: 860px) {
  .app-header {
    display: none;
  }
}
</style>
