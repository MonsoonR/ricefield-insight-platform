<template>
  <PageContainer
    title="场景驾驶舱"
    description="围绕内置稻田数字孪生场景，汇总地块、指标、观测时间、健康状态和预警分布。"
  >
    <template #actions>
      <RouterLink to="/map-twin">
        <a-button type="primary">进入 Cesium 地图</a-button>
      </RouterLink>
    </template>

    <ErrorState v-if="error" :message="error" compact />

    <section v-if="overview" class="panel scene-hero">
      <div>
        <span class="scene-hero__eyebrow">当前数字孪生场景</span>
        <h2>{{ overview.scenario.scenario_name }}</h2>
        <p>{{ overview.scenario.description }}</p>
      </div>
      <div class="scene-hero__score">
        <strong>{{ overview.health_score }}%</strong>
        <span>孪生健康度</span>
      </div>
    </section>

    <div class="page-grid page-grid--four">
      <StatCard
        v-for="card in overviewCards"
        :key="card.label"
        :label="card.label"
        :value="card.value"
        :note="card.note"
        :icon="cardIcon(card.label)"
      />
    </div>

    <div class="page-grid page-grid--two">
      <ChartCard title="区域预警状态" :loading="loading" :empty="!regionStatus.length">
        <EChartView :option="regionOption" :height="300" />
      </ChartCard>
      <ChartCard title="质量状态分布" :loading="loading" :empty="qualityRows.length === 0">
        <EChartView :option="qualityOption" :height="300" />
      </ChartCard>
    </div>

    <div class="page-grid page-grid--two">
      <ChartCard title="默认指标地块排行" :loading="loading" :empty="compareRows.length === 0">
        <EChartView :option="compareOption" :height="300" />
      </ChartCard>
      <section class="panel warning-panel">
        <h2 class="section-title">近期预警</h2>
        <EmptyState v-if="warnings.length === 0" compact description="当前场景暂无预警" />
        <ul v-else class="warning-list">
          <li v-for="item in warnings.slice(0, 6)" :key="item.warning_id">
            <StatusTag :status="item.warning_type" />
            <strong>{{ item.plot_code }} · {{ item.metric_name }}</strong>
            <span>{{ item.observed_at }} · {{ item.message }}</span>
          </li>
        </ul>
      </section>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  AlertOutlined,
  BarChartOutlined,
  CalendarOutlined,
  DashboardOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, ref } from 'vue';

import {
  fetchMetricCompare,
  fetchScenarioOverview,
  fetchWarnings,
  getApiErrorMessage,
} from '@/api';
import {
  ChartCard,
  EChartView,
  EmptyState,
  ErrorState,
  PageContainer,
  StatCard,
  StatusTag,
} from '@/components/base';
import { buildOverviewCards, getOverviewApiErrorMessage } from '@/services/overview';
import { sortMetricCompareRows } from '@/services/twinAnalysis';
import type {
  MetricCompareItem,
  ScenarioOverviewResponse,
  WarningItem,
} from '@/types/api';

const loading = ref(false);
const error = ref('');
const overview = ref<ScenarioOverviewResponse>();
const compareRows = ref<MetricCompareItem[]>([]);
const warnings = ref<WarningItem[]>([]);

const overviewCards = computed(() =>
  overview.value ? buildOverviewCards(overview.value) : [],
);
const regionStatus = computed(() => overview.value?.region_status ?? []);
const qualityRows = computed(() =>
  Object.entries(overview.value?.quality_counts ?? {})
    .filter(([, value]) => value > 0)
    .map(([name, value]) => ({ name: qualityLabel(name), value })),
);

const regionOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 42 },
  xAxis: { type: 'category', data: regionStatus.value.map((item) => item.region) },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f0' } } },
  series: [
    {
      name: '预警数量',
      type: 'bar',
      data: regionStatus.value.map((item) => item.warning_count),
      itemStyle: { color: '#d97706' },
    },
  ],
}));

const qualityOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item' },
  legend: { right: 12, top: 'middle', orient: 'vertical' },
  series: [{
    name: '质量状态',
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['36%', '50%'],
    data: qualityRows.value,
    color: ['#169b62', '#f59e0b', '#ef4444', '#9ca3af'],
  }],
}));

const compareOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 36, left: 42 },
  xAxis: { type: 'category', data: compareRows.value.map((item) => item.plot_code) },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f0' } } },
  series: [{
    name: '指标值',
    type: 'bar',
    data: compareRows.value.map((item) => item.value),
    itemStyle: { color: '#07883f' },
  }],
}));

onMounted(async () => {
  loading.value = true;
  try {
    const overviewData = await fetchScenarioOverview();
    overview.value = overviewData;
    const [compareData, warningData] = await Promise.all([
      fetchMetricCompare({
        metricCode: overviewData.default_metric_code,
        observedAt: overviewData.default_observed_at,
      }),
      fetchWarnings(),
    ]);
    compareRows.value = sortMetricCompareRows(compareData.items).slice(0, 8);
    warnings.value = warningData.items;
  } catch (currentError) {
    error.value = getOverviewApiErrorMessage(
      currentError,
      getApiErrorMessage(currentError, '场景驾驶舱加载失败。'),
    );
  } finally {
    loading.value = false;
  }
});

function cardIcon(label: string) {
  if (label.includes('地块')) {
    return EnvironmentOutlined;
  }
  if (label.includes('指标')) {
    return BarChartOutlined;
  }
  if (label.includes('观测')) {
    return CalendarOutlined;
  }
  if (label.includes('预警')) {
    return AlertOutlined;
  }
  return DashboardOutlined;
}

function qualityLabel(flag: string) {
  const labels: Record<string, string> = {
    normal: '正常',
    missing: '缺失',
    outlier: '异常',
    error: '错误',
  };
  return labels[flag] ?? flag;
}
</script>

<style scoped>
.scene-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 22px 24px;
}

.scene-hero__eyebrow {
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.scene-hero h2 {
  margin: 8px 0;
  color: #13281d;
  font-size: 26px;
}

.scene-hero p {
  margin: 0;
  max-width: 760px;
  color: #52635a;
}

.scene-hero__score {
  text-align: right;
}

.scene-hero__score strong {
  display: block;
  color: #07883f;
  font-size: 42px;
  line-height: 1;
}

.scene-hero__score span {
  display: block;
  margin-top: 8px;
  color: #64748b;
  font-weight: 800;
}

.warning-panel {
  padding: 16px;
}

.warning-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.warning-list li {
  display: grid;
  grid-template-columns: auto 150px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.warning-list span:last-child {
  min-width: 0;
  color: #52635a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
