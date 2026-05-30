<template>
  <PageContainer>
    <ErrorState v-if="error" :message="error" compact />

    <section v-if="overview" class="scene-hero">
      <div class="scene-hero__field" aria-hidden="true">
        <span v-for="row in 9" :key="row" />
      </div>
      <div class="scene-hero__content">
        <span class="scene-hero__tag">当前场景</span>
        <h1>{{ overview.scenario.scenario_id }}</h1>
        <h2>{{ scenarioDisplayName }}</h2>
        <p>基于程序生成的稻田地块、指标和时序观测数据，呈现地块状态、指标趋势、预警风险和地图孪生联动。</p>
        <div class="scene-hero__meta">
          <span><CalendarOutlined />最近观测日期：{{ overview.default_observed_at }}</span>
          <span><EnvironmentOutlined />{{ regionSummary }}</span>
          <span><DatabaseOutlined />模拟观测 · 可追溯批次</span>
        </div>
      </div>
      <div class="scene-hero__decision" :class="`scene-hero__decision--${heroHealthTone}`">
        <span class="scene-hero__decision-label">当前孪生健康度</span>
        <strong>{{ overview.health_score }}%</strong>
        <p>{{ heroSummaryText }}</p>
        <div class="scene-hero__decision-meta">
          <span>{{ heroWarningText }}</span>
          <span>{{ overview.default_observed_at }}</span>
        </div>
        <div class="scene-hero__actions">
          <RouterLink to="/map-twin">
            <a-button type="primary" size="large">
              <EnvironmentOutlined />
              查看地图
            </a-button>
          </RouterLink>
          <RouterLink to="/warnings">
            <a-button size="large">
              <AlertOutlined />
              处理预警
            </a-button>
          </RouterLink>
        </div>
      </div>
    </section>

    <div class="overview-kpis">
      <RouterLink
        v-for="card in supportingOverviewCards"
        :key="card.label"
        :to="cardRoute(card.label)"
        class="kpi-card"
        :class="`kpi-card--${cardTone(card.label)}`"
      >
        <span class="kpi-card__icon">
          <component :is="cardIcon(card.label)" />
        </span>
        <span class="kpi-card__label">{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <small>{{ card.note }}</small>
      </RouterLink>
    </div>

    <section class="key-metrics panel">
      <header class="panel-header">
        <div>
          <h2 class="section-title">关键指标概览</h2>
          <p class="section-subtitle">展示核心稻田指标的最新场景均值、代表地块趋势和质量状态。</p>
        </div>
        <RouterLink to="/metric-compare" class="rf-action-link">进入指标对比</RouterLink>
      </header>
      <EmptyState v-if="!loading && keyMetricCards.length === 0" compact description="暂无关键指标数据" />
      <div v-else class="key-metrics__grid">
        <article
          v-for="metric in keyMetricCards"
          :key="metric.metricCode"
          class="key-metric"
          :class="`key-metric--${metric.statusLevel}`"
        >
          <header>
            <span>{{ metric.name }}</span>
            <StatusTag :status="metric.statusLevel" />
          </header>
          <div class="key-metric__value">
            <strong>{{ metric.value }}</strong>
            <small>{{ metric.unit }}</small>
          </div>
          <p class="key-metric__hint">{{ metricHint(metric.metricCode) }}</p>
          <div class="key-metric__trend" :class="`key-metric__trend--${metric.direction}`">
            <RiseOutlined v-if="metric.direction === 'up'" />
            <FallOutlined v-else-if="metric.direction === 'down'" />
            <LineChartOutlined v-else />
            <span>{{ metric.trendText }}</span>
          </div>
          <svg class="key-metric__sparkline" viewBox="0 0 96 30" role="img" :aria-label="`${metric.name}近7次趋势`">
            <polyline :points="metric.sparklinePoints" />
          </svg>
        </article>
      </div>
    </section>

    <div class="overview-grid">
      <ChartCard
        title="风险状态分布"
        description="按正常、关注、预警、严重四级状态汇总观测质量。"
        :loading="loading"
        :empty="riskDistribution.every((item) => item.value === 0)"
      >
        <template #extra>
          <RouterLink to="/warnings" class="rf-action-link">预警详情</RouterLink>
        </template>
        <div class="risk-layout">
          <EChartView :option="riskOption" :height="260" />
          <div class="risk-list">
            <RouterLink
              v-for="item in riskDistribution"
              :key="item.key"
              to="/warnings"
              class="risk-list__item"
              :class="`risk-list__item--${item.key}`"
            >
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </RouterLink>
          </div>
        </div>
      </ChartCard>

      <ChartCard
        title="区域状态"
        description="试验一区、试验二区的地块数量和预警数量。"
        :loading="loading"
        :empty="!regionStatus.length"
      >
        <template #extra>
          <RouterLink to="/map-twin" class="rf-action-link">地图定位</RouterLink>
        </template>
        <div class="region-layout">
          <EChartView :option="regionOption" :height="240" />
          <div class="region-cards">
            <RouterLink
              v-for="item in regionStatus"
              :key="item.region"
              to="/map-twin"
              class="region-card"
            >
              <span>{{ item.region }}</span>
              <strong>{{ item.plot_count }} 块</strong>
              <small>{{ item.warning_count }} 条预警</small>
            </RouterLink>
          </div>
        </div>
      </ChartCard>
    </div>

    <section class="focus-panel panel">
      <header class="panel-header">
        <div>
          <h2 class="section-title">重点关注地块</h2>
          <p class="section-subtitle">根据近期质量问题聚合，点击地块进入地块画像。</p>
        </div>
        <RouterLink to="/warnings" class="rf-action-link">查看全部预警</RouterLink>
      </header>
      <EmptyState v-if="focusPlots.length === 0" compact description="当前场景暂无重点关注地块" />
      <div v-else class="focus-grid">
        <RouterLink
          v-for="item in focusPlots"
          :key="item.plotId"
          :to="{ name: 'plot-detail', params: { plotId: item.plotId } }"
          class="focus-plot"
        >
          <span class="focus-plot__code">{{ item.plotCode }}</span>
          <span class="focus-plot__name">{{ item.plotName }}</span>
          <span class="focus-plot__meta">{{ item.region }} · {{ item.latestDate }}</span>
          <strong>{{ item.warningCount }} 条预警</strong>
        </RouterLink>
      </div>
    </section>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  AlertOutlined,
  AppstoreOutlined,
  BarChartOutlined,
  CalendarOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  EnvironmentOutlined,
  FallOutlined,
  FundOutlined,
  LineChartOutlined,
  RiseOutlined,
} from '@ant-design/icons-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, ref } from 'vue';

import {
  fetchMetricCompare,
  fetchMetrics,
  fetchPlotSeries,
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
  StatusTag,
} from '@/components/base';
import {
  buildOverviewCards,
  buildRiskDistribution,
  getOverviewApiErrorMessage,
} from '@/services/overview';
import { mapQualityToStatus, type StatusLevel } from '@/utils/status';
import type {
  Metric,
  MetricCompareItem,
  MetricCompareResponse,
  PlotSeriesResponse,
  ScenarioOverviewResponse,
  WarningItem,
} from '@/types/api';

interface KeyMetricCard {
  metricCode: string;
  name: string;
  value: string;
  unit: string;
  statusLevel: StatusLevel;
  direction: 'up' | 'down' | 'flat';
  trendText: string;
  sparklinePoints: string;
}

interface FocusPlot {
  plotId: string;
  plotCode: string;
  plotName: string;
  region: string;
  latestDate: string;
  warningCount: number;
}

const CORE_METRIC_CODES = ['crop_growth', 'chlorophyll', 'nitrogen', 'ph', 'leaf_area_index'];
const STATUS_HEX: Record<StatusLevel, string> = {
  normal: '#16a36a',
  watch: '#c58b04',
  warning: '#ea580c',
  critical: '#dc2626',
  empty: '#9ca3af',
};

const loading = ref(false);
const error = ref('');
const overview = ref<ScenarioOverviewResponse>();
const keyMetricCards = ref<KeyMetricCard[]>([]);
const warnings = ref<WarningItem[]>([]);

const overviewCards = computed(() =>
  overview.value ? buildOverviewCards(overview.value) : [],
);
const supportingOverviewCards = computed(() =>
  overviewCards.value.filter((card) => card.label !== '孪生健康度'),
);
const regionStatus = computed(() => overview.value?.region_status ?? []);
const riskDistribution = computed(() =>
  buildRiskDistribution(overview.value?.quality_counts ?? {}),
);

const scenarioDisplayName = computed(() => {
  const name = overview.value?.scenario.scenario_name ?? '稻田数字孪生演示场景';
  return name.replace(/\s*2025$/, '');
});

const regionSummary = computed(() => {
  if (!regionStatus.value.length) {
    return '试验地块';
  }
  const total = regionStatus.value.reduce((sum, item) => sum + item.plot_count, 0);
  return `${regionStatus.value.length} 个试验区 · ${total} 块地块`;
});

const warningCount = computed(() => {
  const warningCard = overviewCards.value.find((card) => card.label.includes('预警'));
  return Number.parseInt(warningCard?.value ?? '0', 10) || 0;
});

const heroHealthTone = computed<StatusLevel>(() => {
  const score = overview.value?.health_score ?? 0;
  if (score >= 90) {
    return 'normal';
  }
  if (score >= 75) {
    return 'watch';
  }
  if (score >= 60) {
    return 'warning';
  }
  return 'critical';
});

const heroSummaryText = computed(() => {
  const count = warningCount.value;
  if (count === 0) {
    return '当前场景整体稳定，可继续查看地图和指标趋势。';
  }
  return `整体状态可演示，但有 ${count} 条质量预警需要优先核查。`;
});

const heroWarningText = computed(() =>
  warningCount.value > 0 ? `${warningCount.value} 条预警待核查` : '暂无待处理预警',
);

const focusPlots = computed<FocusPlot[]>(() => {
  const grouped = new Map<string, FocusPlot>();
  warnings.value.forEach((item) => {
    const current = grouped.get(item.plot_id);
    if (!current) {
      grouped.set(item.plot_id, {
        plotId: item.plot_id,
        plotCode: item.plot_code,
        plotName: item.plot_name ?? item.plot_code,
        region: item.region ?? '未分区',
        latestDate: item.observed_at,
        warningCount: 1,
      });
      return;
    }
    current.warningCount += 1;
    if (item.observed_at > current.latestDate) {
      current.latestDate = item.observed_at;
    }
  });

  return Array.from(grouped.values())
    .sort((left, right) => right.warningCount - left.warningCount || right.latestDate.localeCompare(left.latestDate))
    .slice(0, 4);
});

const riskOption = computed<EChartsOption>(() => ({
  color: riskDistribution.value.map((item) => getStatusHex(item.key)),
  tooltip: {
    trigger: 'item',
    backgroundColor: '#ffffff',
    borderColor: '#edf2ef',
    textStyle: { color: '#1f2937' },
  },
  legend: { show: false },
  series: [{
    name: '风险状态',
    type: 'pie',
    radius: ['58%', '78%'],
    center: ['50%', '50%'],
    avoidLabelOverlap: true,
    label: { show: false },
    itemStyle: { borderColor: '#ffffff', borderWidth: 3 },
    data: riskDistribution.value.map((item) => ({
      name: item.label,
      value: item.value,
      itemStyle: { color: getStatusHex(item.key) },
    })),
  }],
}));

const regionOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#edf2ef',
    textStyle: { color: '#1f2937' },
  },
  grid: { top: 24, right: 18, bottom: 32, left: 42 },
  legend: {
    top: 0,
    right: 0,
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

onMounted(async () => {
  loading.value = true;
  try {
    const overviewData = await fetchScenarioOverview();
    overview.value = overviewData;

    const [metricsData, warningData, ...compareData] = await Promise.all([
      fetchMetrics(),
      fetchWarnings(),
      ...CORE_METRIC_CODES.map((metricCode) =>
        fetchMetricCompare({
          metricCode,
          observedAt: overviewData.default_observed_at,
        }),
      ),
    ]);

    warnings.value = warningData.items
      .slice()
      .sort((left, right) => right.observed_at.localeCompare(left.observed_at));

    const seriesData = await Promise.all(
      compareData.map((metricCompare) => {
        const representative = metricCompare.items.find((item) => typeof item.value === 'number')
          ?? metricCompare.items[0];
        if (!representative) {
          return Promise.resolve(undefined);
        }
        return fetchPlotSeries({
          plotId: representative.plot_id,
          metricCode: metricCompare.metric_code,
        }).catch(() => undefined);
      }),
    );

    keyMetricCards.value = compareData.map((metricCompare, index) =>
      buildKeyMetricCard(
        metricCompare,
        metricsData.items.find((item) => item.metric_code === metricCompare.metric_code),
        seriesData[index],
      ),
    );
  } catch (currentError) {
    error.value = getOverviewApiErrorMessage(
      currentError,
      getApiErrorMessage(currentError, '场景驾驶舱加载失败。'),
    );
  } finally {
    loading.value = false;
  }
});

function buildKeyMetricCard(
  metricCompare: MetricCompareResponse,
  metric: Metric | undefined,
  seriesResponse: PlotSeriesResponse | undefined,
): KeyMetricCard {
  const numericRows = metricCompare.items.filter((item): item is MetricCompareItem & { value: number } =>
    typeof item.value === 'number',
  );
  const average = numericRows.length
    ? numericRows.reduce((sum, item) => sum + item.value, 0) / numericRows.length
    : 0;
  const displayValue = normalizeMetricValue(metricCompare.metric_code, average);
  const statusLevel = worstStatus(metricCompare.items.map((item) => mapQualityToStatus(item.quality_flag)));
  const points = seriesResponse?.series
    .find((item) => item.metric_code === metricCompare.metric_code)
    ?.points
    .filter((point) => typeof point.value === 'number')
    .slice(-7)
    .map((point) => normalizeMetricValue(metricCompare.metric_code, point.value as number)) ?? [];

  const first = points[0] ?? displayValue;
  const last = points[points.length - 1] ?? displayValue;
  const delta = first === 0 ? 0 : ((last - first) / Math.abs(first)) * 100;

  return {
    metricCode: metricCompare.metric_code,
    name: metric?.metric_name ?? metricCompare.metric_name,
    value: formatMetricNumber(displayValue, metric?.precision),
    unit: metric?.unit ?? metricCompare.items[0]?.unit ?? '',
    statusLevel,
    direction: delta > 0.1 ? 'up' : delta < -0.1 ? 'down' : 'flat',
    trendText: Math.abs(delta) < 0.1 ? '近7次持平' : `近7次 ${delta > 0 ? '+' : ''}${delta.toFixed(1)}%`,
    sparklinePoints: buildSparklinePoints(points.length ? points : [displayValue]),
  };
}

function normalizeMetricValue(metricCode: string, value: number): number {
  if (metricCode === 'crop_growth') {
    return value * 100;
  }
  return value;
}

function formatMetricNumber(value: number, precision = 2): string {
  const fixed = value >= 20 ? 1 : precision;
  return Number(value.toFixed(fixed)).toString();
}

function worstStatus(levels: StatusLevel[]): StatusLevel {
  const weight: Record<StatusLevel, number> = {
    empty: 0,
    normal: 1,
    watch: 2,
    warning: 3,
    critical: 4,
  };
  return levels.reduce((current, next) => (weight[next] > weight[current] ? next : current), 'normal');
}

function buildSparklinePoints(values: number[]): string {
  if (!values.length) {
    return '4,26 92,26';
  }
  const width = 88;
  const height = 22;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return values.map((value, index) => {
    const x = 4 + (values.length === 1 ? width : (index / (values.length - 1)) * width);
    const y = 4 + height - ((value - min) / range) * height;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
}

function cardRoute(label: string) {
  if (label.includes('预警')) {
    return '/warnings';
  }
  if (label.includes('地块') || label.includes('健康')) {
    return '/map-twin';
  }
  if (label.includes('指标')) {
    return '/metric-compare';
  }
  return '/overview';
}

function cardIcon(label: string) {
  if (label.includes('地块')) {
    return AppstoreOutlined;
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
  if (label.includes('健康')) {
    return FundOutlined;
  }
  return DashboardOutlined;
}

function cardTone(label: string): 'green' | 'cyan' | 'purple' | 'orange' | 'blue' {
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
  return 'blue';
}

function getStatusHex(level: StatusLevel): string {
  return STATUS_HEX[level] ?? STATUS_HEX.empty;
}

function metricHint(metricCode: string) {
  const hints: Record<string, string> = {
    crop_growth: '长势评分直接影响演示结论',
    chlorophyll: '反映叶片活力与氮素吸收',
    nitrogen: '用于判断土壤养分风险',
    ph: '用于识别酸碱环境偏离',
    leaf_area_index: '衡量冠层覆盖与生长量',
  };
  return hints[metricCode] ?? '核心观测指标';
}
</script>

<style scoped>
.scene-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  min-height: 238px;
  overflow: hidden;
  border-radius: var(--rf-radius-lg);
  background:
    linear-gradient(90deg, rgba(4, 74, 51, 0.92), rgba(11, 107, 69, 0.78) 48%, rgba(21, 144, 93, 0.58)),
    linear-gradient(180deg, #e8f6ef, #bfe6ce);
  box-shadow: 0 16px 32px rgba(15, 56, 37, 0.14);
  gap: 28px;
  padding: 28px 32px;
}

.scene-hero::before,
.scene-hero::after {
  position: absolute;
  content: "";
  pointer-events: none;
}

.scene-hero::before {
  inset: auto -8% -34% -8%;
  height: 70%;
  background:
    repeating-linear-gradient(92deg, rgba(255, 255, 255, 0.14) 0 2px, transparent 2px 42px),
    repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.10) 0 1px, transparent 1px 28px);
  transform: perspective(520px) rotateX(58deg);
  transform-origin: bottom;
}

.scene-hero::after {
  inset: 0;
  background:
    radial-gradient(circle at 68% 20%, rgba(255, 255, 255, 0.28), transparent 26%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.08), transparent 42%);
}

.scene-hero__field {
  position: absolute;
  inset: auto 0 0;
  display: grid;
  gap: 10px;
  height: 88px;
  padding: 0 32px 16px;
  opacity: 0.55;
}

.scene-hero__field span {
  border-top: 1px solid rgba(255, 255, 255, 0.32);
  transform: skewX(-24deg);
}

.scene-hero__content,
.scene-hero__decision,
.scene-hero__actions {
  position: relative;
  z-index: 1;
}

.scene-hero__tag {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: var(--rf-radius);
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 700;
  padding: 4px 10px;
}

.scene-hero h1,
.scene-hero h2,
.scene-hero p {
  color: #ffffff;
}

.scene-hero h1 {
  margin: 16px 0 6px;
  font-size: 40px;
  font-weight: 800;
  line-height: 1.08;
}

.scene-hero h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.25;
}

.scene-hero p {
  max-width: 720px;
  margin: 16px 0 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: 14px;
  line-height: 1.7;
}

.scene-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 18px;
  color: rgba(255, 255, 255, 0.92);
  font-size: 13px;
}

.scene-hero__meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.scene-hero__decision {
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
  padding: 20px;
  backdrop-filter: blur(10px);
}

.scene-hero__decision-label {
  color: rgba(255, 255, 255, 0.82);
  font-size: 13px;
  font-weight: 700;
}

.scene-hero__decision strong {
  margin-top: 6px;
  color: #ffffff;
  font-size: 54px;
  font-weight: 800;
  line-height: 1;
}

.scene-hero__decision p {
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 1.6;
}

.scene-hero__decision-meta {
  display: grid;
  gap: 6px;
  margin-top: 12px;
  color: rgba(255, 255, 255, 0.86);
  font-size: 12px;
  font-weight: 700;
}

.scene-hero__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 16px;
}

.scene-hero__actions :deep(.ant-btn) {
  width: 100%;
  height: 40px;
  border-color: rgba(255, 255, 255, 0.36);
  box-shadow: none;
  font-weight: 700;
}

.scene-hero__actions :deep(.ant-btn:not(.ant-btn-primary)) {
  background: rgba(255, 255, 255, 0.9);
  color: var(--rf-primary-dark);
}

.overview-kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.kpi-card {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  grid-template-rows: auto auto auto;
  gap: 2px 14px;
  min-height: 116px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: linear-gradient(180deg, #ffffff, #fbfdfc);
  box-shadow: var(--rf-shadow);
  color: inherit;
  padding: 18px 20px;
  text-decoration: none;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}

.kpi-card:hover {
  border-color: color-mix(in srgb, var(--tone) 32%, var(--rf-border-soft));
  box-shadow: 0 10px 24px rgba(15, 56, 37, 0.10);
  transform: translateY(-2px);
}

.kpi-card__icon {
  display: grid;
  grid-row: 1 / span 3;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 50%;
  background: color-mix(in srgb, var(--tone) 14%, white);
  color: var(--tone);
  font-size: 19px;
}

.kpi-card__label {
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.35;
}

.kpi-card strong {
  color: var(--rf-text);
  font-size: 32px;
  font-weight: 800;
  line-height: 1.08;
}

.kpi-card small {
  min-width: 0;
  color: var(--rf-text-soft);
  font-size: 12px;
  line-height: 1.45;
}

.kpi-card--green {
  --tone: var(--rf-primary);
}

.kpi-card--cyan {
  --tone: var(--rf-accent-cyan);
}

.kpi-card--purple {
  --tone: var(--rf-purple);
}

.kpi-card--orange {
  --tone: var(--rf-status-warning);
}

.kpi-card--blue {
  --tone: var(--rf-info);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--rf-border-soft);
  padding: 16px 20px 14px;
}

.key-metrics {
  overflow: hidden;
}

.key-metrics__grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  padding: 16px 20px 20px;
}

.key-metric {
  position: relative;
  min-width: 0;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius);
  background: var(--rf-surface-soft);
  padding: 16px;
  overflow: hidden;
}

.key-metric::before {
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: currentColor;
  content: "";
}

.key-metric header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.key-metric__value {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 12px;
}

.key-metric__value strong {
  color: var(--rf-text);
  font-size: 28px;
  font-weight: 800;
  line-height: 1.05;
}

.key-metric__value small {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.key-metric__hint {
  min-height: 36px;
  margin: 8px 0 0;
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.5;
}

.key-metric__trend {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 10px;
  font-size: 12px;
  font-weight: 700;
}

.key-metric__trend--up {
  color: var(--rf-status-normal);
}

.key-metric__trend--down {
  color: var(--rf-status-warning);
}

.key-metric__trend--flat {
  color: var(--rf-text-muted);
}

.key-metric__sparkline {
  width: 100%;
  height: 30px;
  margin-top: 12px;
}

.key-metric__sparkline polyline {
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.4;
}

.key-metric--normal {
  color: var(--rf-status-normal);
}

.key-metric--watch {
  color: var(--rf-status-watch);
}

.key-metric--warning {
  color: var(--rf-status-warning);
}

.key-metric--critical {
  color: var(--rf-status-critical);
}

.key-metric--empty {
  color: var(--rf-status-empty);
}

.overview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
}

.risk-layout,
.region-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px;
  align-items: center;
  gap: 16px;
}

.risk-list,
.region-cards {
  display: grid;
  gap: 10px;
}

.risk-list__item,
.region-card,
.focus-plot {
  color: inherit;
  text-decoration: none;
}

.risk-list__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--status-line);
  border-radius: var(--rf-radius);
  background: var(--status-bg);
  color: var(--status);
  padding: 10px 12px;
}

.risk-list__item span {
  font-size: 13px;
  font-weight: 700;
}

.risk-list__item strong {
  color: var(--rf-text);
  font-size: 20px;
  font-weight: 800;
}

.risk-list__item--normal {
  --status: var(--rf-status-normal);
  --status-bg: var(--rf-status-normal-bg);
  --status-line: var(--rf-status-normal-line);
}

.risk-list__item--watch {
  --status: var(--rf-status-watch);
  --status-bg: var(--rf-status-watch-bg);
  --status-line: var(--rf-status-watch-line);
}

.risk-list__item--warning {
  --status: var(--rf-status-warning);
  --status-bg: var(--rf-status-warning-bg);
  --status-line: var(--rf-status-warning-line);
}

.risk-list__item--critical {
  --status: var(--rf-status-critical);
  --status-bg: var(--rf-status-critical-bg);
  --status-line: var(--rf-status-critical-line);
}

.region-card {
  display: grid;
  gap: 2px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius);
  background: var(--rf-surface-soft);
  padding: 10px 12px;
}

.region-card span {
  color: var(--rf-text-muted);
  font-size: 12px;
  font-weight: 700;
}

.region-card strong {
  color: var(--rf-text);
  font-size: 20px;
  font-weight: 800;
}

.region-card small {
  color: var(--rf-status-warning);
  font-size: 12px;
  font-weight: 700;
}

.focus-panel {
  overflow: hidden;
}

.focus-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  padding: 16px 20px 20px;
}

.focus-plot {
  display: grid;
  gap: 6px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius);
  background: linear-gradient(180deg, #ffffff, var(--rf-surface-soft));
  padding: 14px;
}

.focus-plot:hover {
  border-color: var(--rf-primary-line);
}

.focus-plot__code {
  color: var(--rf-primary-dark);
  font-size: 20px;
  font-weight: 800;
  line-height: 1.1;
}

.focus-plot__name,
.focus-plot__meta {
  overflow: hidden;
  color: var(--rf-text-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.focus-plot strong {
  color: var(--rf-status-warning);
  font-size: 13px;
  font-weight: 800;
}

@media (max-width: 1280px) {
  .overview-kpis,
  .key-metrics__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .focus-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1080px) {
  .scene-hero,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .scene-hero {
    gap: 20px;
  }
}

@media (max-width: 720px) {
  .scene-hero {
    padding: 24px 20px;
  }

  .scene-hero h1 {
    font-size: 30px;
  }

  .scene-hero h2 {
    font-size: 20px;
  }

  .overview-kpis,
  .key-metrics__grid,
  .focus-grid,
  .risk-layout,
  .region-layout {
    grid-template-columns: 1fr;
  }

  .panel-header {
    display: block;
  }

  .panel-header .rf-action-link {
    display: inline-block;
    margin-top: 10px;
  }
}
</style>
