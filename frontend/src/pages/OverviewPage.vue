<template>
  <PageContainer>
    <ErrorState v-if="error" :message="error" compact />

    <section v-if="overview" class="scene-hero">
      <div class="scene-hero__media" aria-hidden="true">
        <div class="scene-hero__pattern" />
        <div class="scene-hero__badge">
          <DashboardOutlined />
          <span>数字孪生场景</span>
        </div>
      </div>
      <div class="scene-hero__content">
        <span class="scene-hero__tag">当前演示场景</span>
        <h2>{{ overview.scenario.scenario_name }}</h2>
        <p>{{ overview.scenario.description }}</p>
        <div class="scene-hero__meta">
          <span><EnvironmentOutlined />{{ regionSummary }}</span>
          <span><CalendarOutlined />{{ observationRange }}</span>
          <span><DatabaseOutlined />演示数据 · 后端程序生成</span>
        </div>
      </div>
      <div class="scene-hero__score">
        <div class="scene-hero__score-ring">
          <strong>{{ overview.health_score }}</strong>
          <small>%</small>
        </div>
        <span>孪生健康度</span>
        <RouterLink to="/map-twin">
          <a-button type="primary" size="small">进入地图</a-button>
        </RouterLink>
      </div>
    </section>

    <div class="page-grid page-grid--four">
      <StatCard
        v-for="card in overviewCards"
        :key="card.label"
        :label="card.label"
        :value="card.value"
        :note="card.note"
        :tone="cardTone(card.label)"
        :icon="cardIcon(card.label)"
      />
    </div>

    <div class="overview-grid">
      <ChartCard
        title="区域状态对比"
        description="按试验区分布的地块数量与预警数量"
        :loading="loading"
        :empty="!regionStatus.length"
      >
        <EChartView :option="regionOption" :height="300" />
      </ChartCard>

      <section class="warning-panel panel">
        <header class="warning-panel__header">
          <div>
            <h2 class="section-title">近期预警</h2>
            <p class="section-subtitle">最近 6 条状态变化</p>
          </div>
          <RouterLink to="/warnings" class="warning-panel__more">查看全部</RouterLink>
        </header>
        <EmptyState v-if="warnings.length === 0" compact description="当前场景暂无预警" />
        <ul v-else class="warning-list">
          <li v-for="item in warnings.slice(0, 6)" :key="item.warning_id">
            <StatusTag :status="item.warning_type" />
            <div class="warning-list__body">
              <strong>{{ item.plot_code }} · {{ item.metric_name }}</strong>
              <span>{{ item.message }}</span>
            </div>
            <small>{{ item.observed_at }}</small>
          </li>
        </ul>
      </section>
    </div>

    <div class="page-grid page-grid--two">
      <ChartCard
        :title="`${rankMetricName}地块排行`"
        description="默认指标在各试验地块上的最新观测值"
        :loading="loading"
        :empty="compareRows.length === 0"
      >
        <EChartView :option="compareOption" :height="300" />
      </ChartCard>

      <ChartCard
        title="数据质量状态分布"
        description="所有观测记录按质量标记的统计"
        :loading="loading"
        :empty="qualityRows.length === 0"
      >
        <EChartView :option="qualityOption" :height="300" />
      </ChartCard>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  AlertOutlined,
  BarChartOutlined,
  CalendarOutlined,
  DashboardOutlined,
  DatabaseOutlined,
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
import { mapQualityToStatus, statusLevelMeta, type StatusLevel } from '@/utils/status';
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
    .map(([flag, value]) => {
      const level = mapQualityToStatus(flag);
      return {
        name: statusLevelMeta[level].label,
        value,
        itemStyle: { color: getStatusHex(level) },
      };
    }),
);

const rankMetricName = computed(() => {
  const code = overview.value?.default_metric_code;
  if (!code) {
    return '默认指标';
  }
  return code === 'crop_growth' ? '作物长势' : code;
});

const regionSummary = computed(() => {
  if (!regionStatus.value.length) {
    return '试验地块';
  }
  const total = regionStatus.value.reduce((sum, item) => sum + item.plot_count, 0);
  return `${regionStatus.value.length} 个试验区 · ${total} 块地块`;
});

const observationRange = computed(() => {
  const date = overview.value?.default_observed_at;
  return date ? `最新观测 ${date}` : '暂无观测日期';
});

const regionOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#edf2ef',
    textStyle: { color: '#1f2937' },
  },
  grid: { top: 36, right: 24, bottom: 36, left: 48 },
  legend: {
    top: 4,
    textStyle: { color: '#6b7280' },
    itemWidth: 10,
    itemHeight: 10,
  },
  xAxis: {
    type: 'category',
    data: regionStatus.value.map((item) => item.region),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#6b7280' },
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: '#edf2ef' } },
    axisLabel: { color: '#9ca3af' },
  },
  series: [
    {
      name: '地块数量',
      type: 'bar',
      barWidth: 28,
      itemStyle: { color: '#15905d', borderRadius: [4, 4, 0, 0] },
      data: regionStatus.value.map((item) => item.plot_count),
    },
    {
      name: '预警数量',
      type: 'bar',
      barWidth: 28,
      itemStyle: { color: '#ea580c', borderRadius: [4, 4, 0, 0] },
      data: regionStatus.value.map((item) => item.warning_count),
    },
  ],
}));

const qualityOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: '#ffffff',
    borderColor: '#edf2ef',
    textStyle: { color: '#1f2937' },
  },
  legend: { right: 12, top: 'middle', orient: 'vertical', textStyle: { color: '#6b7280' } },
  series: [{
    name: '质量状态',
    type: 'pie',
    radius: ['54%', '76%'],
    center: ['38%', '50%'],
    avoidLabelOverlap: true,
    label: { show: false },
    itemStyle: { borderColor: '#ffffff', borderWidth: 2 },
    data: qualityRows.value,
  }],
}));

const compareOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#edf2ef',
    textStyle: { color: '#1f2937' },
  },
  grid: { top: 24, right: 24, bottom: 36, left: 48 },
  xAxis: {
    type: 'category',
    data: compareRows.value.map((item) => item.plot_code),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#6b7280' },
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: '#edf2ef' } },
    axisLabel: { color: '#9ca3af' },
  },
  series: [{
    name: '指标值',
    type: 'bar',
    barWidth: 28,
    data: compareRows.value.map((item) => ({
      value: item.value,
      itemStyle: {
        color: getStatusHex(mapQualityToStatus(item.quality_flag)),
        borderRadius: [4, 4, 0, 0],
      },
    })),
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

function cardTone(label: string): 'green' | 'cyan' | 'purple' | 'orange' {
  if (label.includes('地块')) {
    return 'green';
  }
  if (label.includes('指标')) {
    return 'cyan';
  }
  if (label.includes('观测')) {
    return 'purple';
  }
  if (label.includes('预警')) {
    return 'orange';
  }
  return 'green';
}

function getStatusHex(level: StatusLevel): string {
  const map: Record<StatusLevel, string> = {
    normal: '#16a36a',
    watch: '#c58b04',
    warning: '#ea580c',
    critical: '#dc2626',
    empty: '#9ca3af',
  };
  return map[level] ?? '#9ca3af';
}
</script>

<style scoped>
.scene-hero {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: 24px;
  overflow: hidden;
  border: 1px solid var(--rf-primary-line);
  border-radius: var(--rf-radius-lg);
  background:
    linear-gradient(135deg, var(--rf-primary-soft) 0%, #ffffff 65%);
  box-shadow: var(--rf-shadow);
  padding: 22px 26px;
}

.scene-hero__media {
  position: relative;
  flex: 0 0 200px;
  border-radius: 10px;
  overflow: hidden;
  min-height: 132px;
  background:
    linear-gradient(150deg, var(--rf-primary) 0%, var(--rf-primary-darker) 100%);
}

.scene-hero__pattern {
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(115deg, rgba(255, 255, 255, 0.16) 0 4px, transparent 4px 28px),
    radial-gradient(circle at 75% 25%, rgba(255, 255, 255, 0.32), transparent 60%);
}

.scene-hero__badge {
  position: absolute;
  left: 14px;
  bottom: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--rf-primary-dark);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
}

.scene-hero__badge :deep(svg) {
  font-size: 13px;
}

.scene-hero__content {
  flex: 1;
  min-width: 0;
}

.scene-hero__tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(21, 144, 93, 0.12);
  color: var(--rf-primary-dark);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
}

.scene-hero h2 {
  margin: 12px 0 6px;
  color: var(--rf-text);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.scene-hero p {
  margin: 0 0 12px;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.6;
  max-width: 640px;
}

.scene-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--rf-text-muted);
  font-size: 12px;
}

.scene-hero__meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.scene-hero__meta :deep(svg) {
  color: var(--rf-primary);
  font-size: 14px;
}

.scene-hero__score {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-left: 1px solid var(--rf-primary-line);
  padding-left: 24px;
  flex: 0 0 auto;
}

.scene-hero__score-ring {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  color: var(--rf-primary);
}

.scene-hero__score-ring strong {
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -1px;
}

.scene-hero__score-ring small {
  font-size: 16px;
  font-weight: 700;
}

.scene-hero__score > span {
  color: var(--rf-text-muted);
  font-size: 13px;
  font-weight: 600;
}

.overview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.6fr);
  gap: 16px;
}

.warning-panel {
  display: flex;
  flex-direction: column;
  padding: 16px 20px 18px;
}

.warning-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid var(--rf-border-soft);
  margin: 0 -20px 12px;
  padding: 0 20px 12px;
}

.warning-panel__more {
  color: var(--rf-primary);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}

.warning-panel__more:hover {
  color: var(--rf-primary-hover);
}

.warning-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.warning-list li {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
}

.warning-list__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.warning-list__body strong {
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.3;
}

.warning-list__body span {
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.warning-list li small {
  color: var(--rf-text-soft);
  font-size: 11px;
  white-space: nowrap;
}

@media (max-width: 1080px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  .scene-hero {
    flex-wrap: wrap;
  }
  .scene-hero__score {
    border-left: 0;
    border-top: 1px solid var(--rf-primary-line);
    padding-left: 0;
    padding-top: 16px;
    flex-direction: row;
    width: 100%;
  }
}
</style>
