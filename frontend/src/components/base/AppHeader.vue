<template>
  <header class="app-header">
    <div class="app-header__filters" aria-label="全局数据状态">
      <label>
        <span>当前场景</span>
        <a-tooltip title="第一阶段固定使用内置数字孪生演示场景">
          <a-select
            v-model:value="selectedScenario"
            :options="scenarioOptions"
            disabled
            placeholder="演示场景"
          />
        </a-tooltip>
      </label>
      <label>
        <span>最新日期</span>
        <a-tooltip title="全局日期筛选暂未接入，请使用页面内筛选栏">
          <a-select
            v-model:value="selectedDate"
            :options="dateOptions"
            disabled
            placeholder="最新日期"
          />
        </a-tooltip>
      </label>
      <label>
        <span>区域</span>
        <a-tooltip title="全局区域筛选暂未接入，请使用页面内筛选栏">
          <RegionSelector v-model="selectedRegion" disabled />
        </a-tooltip>
      </label>
      <label>
        <span>默认指标</span>
        <a-tooltip title="全局指标筛选暂未接入，请使用页面内筛选栏">
          <MetricSelector
            v-model="selectedMetric"
            :options="metricOptions"
            disabled
            placeholder="选择指标"
          />
        </a-tooltip>
      </label>
    </div>
    <div class="app-header__actions">
      <RouterLink to="/map-twin">
        <a-button type="primary">
          <EnvironmentOutlined />
          打开地图
        </a-button>
      </RouterLink>
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
        <strong>研究员</strong>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import {
  BellOutlined,
  EnvironmentOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue';
import { computed, onMounted, ref } from 'vue';

import { fetchCurrentScenario, fetchDates, fetchMetrics, fetchWarnings } from '@/api';
import MetricSelector from '@/components/base/MetricSelector.vue';
import RegionSelector from '@/components/base/RegionSelector.vue';
import type { RegionCode } from '@/types/api';

const selectedScenario = ref<string>('demo-ricefield-2025');
const selectedDate = ref<string>();
const selectedRegion = ref<RegionCode>('all');
const selectedMetric = ref<string>();
const alertCount = ref(0);

const scenarios = ref<Array<{ label: string; value: string }>>([]);
const dates = ref<string[]>([]);
const metrics = ref<Array<{ label: string; value: string; unit?: string }>>([]);

const scenarioOptions = computed(() => scenarios.value);
const dateOptions = computed(() =>
  dates.value.map((date) => ({ label: date, value: date })),
);
const metricOptions = computed(() => metrics.value);

onMounted(async () => {
  const [scenarioResponse, datesResponse, metricsResponse, warningsResponse] = await Promise.allSettled([
    fetchCurrentScenario(),
    fetchDates(),
    fetchMetrics(),
    fetchWarnings(),
  ]);

  if (scenarioResponse.status === 'fulfilled') {
    selectedScenario.value = scenarioResponse.value.scenario_id;
    scenarios.value = [{
      label: scenarioResponse.value.scenario_name,
      value: scenarioResponse.value.scenario_id,
    }];
  }
  if (datesResponse.status === 'fulfilled') {
    dates.value = datesResponse.value.items;
    selectedDate.value = datesResponse.value.items[datesResponse.value.items.length - 1];
  }
  if (metricsResponse.status === 'fulfilled') {
    metrics.value = metricsResponse.value.items.map((item) => ({
      label: item.metric_name,
      value: item.metric_code,
      unit: item.unit,
    }));
    selectedMetric.value = metricsResponse.value.items[0]?.metric_code;
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
  border-bottom: 1px solid var(--rf-border-soft);
  background: rgba(255, 255, 255, 0.92);
  padding: 0 24px;
  backdrop-filter: blur(14px);
}

.app-header__filters {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  align-items: center;
  gap: 18px;
  min-width: 0;
}

.app-header label {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.app-header label > span {
  flex: 0 0 auto;
  color: #223548;
  font-size: 13px;
  font-weight: 800;
}

.app-header :deep(.ant-select) {
  min-width: 150px;
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 16px;
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
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 900;
}

.app-header__user strong {
  white-space: nowrap;
  font-size: 14px;
}

@media (max-width: 1180px) {
  .app-header__filters label:nth-child(-n + 2) {
    display: none;
  }
}

@media (max-width: 860px) {
  .app-header {
    display: none;
  }
}
</style>
