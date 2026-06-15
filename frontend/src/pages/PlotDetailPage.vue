<template>
  <PageContainer
    :title="pageTitle"
    description="全面了解单个地块的基础信息、指标状态与变化趋势。"
  >
    <template #actions>
      <a-button @click="returnToMap">
        <RollbackOutlined />
        返回地图
      </a-button>
    </template>

    <section v-if="plotNotFound" class="plot-empty panel">
      <EmptyState compact description="未找到对应地块，请返回地图选择一个可用地块。" />
      <a-button type="primary" @click="returnToMap">
        <EnvironmentOutlined />
        返回地图
      </a-button>
    </section>

    <ErrorState v-else-if="error" :message="error" compact />

    <section v-if="summary" class="plot-summary panel">
      <div class="plot-summary__identity">
        <div class="plot-summary__id">
          <strong>{{ summary.plot.plot_code }}</strong>
          <StatusTag :status="plotOverallStatus" />
        </div>
        <h2>{{ summary.plot.plot_name || summary.plot.plot_code }}</h2>
        <span class="plot-summary__region">
          <EnvironmentOutlined />
          {{ summary.plot.region || '--' }}
        </span>
      </div>
      <div class="plot-summary__facts">
        <div v-for="fact in summaryFacts" :key="fact.label" class="plot-summary__fact">
          <span>{{ fact.label }}</span>
          <strong :title="fact.value">{{ fact.value }}</strong>
        </div>
      </div>
      <div class="plot-summary__actions">
        <RouterLink :to="mapTwinLocation">
          <a-button type="primary">
            <AimOutlined />
            定位到地图
          </a-button>
        </RouterLink>
      </div>
    </section>

    <div class="plot-body">
      <aside class="plot-info panel">
        <h3 class="section-title">基础信息</h3>
        <dl class="info-list">
          <div><dt>地块编号</dt><dd>{{ summary?.plot.plot_code || '--' }}</dd></div>
          <div><dt>地块名称</dt><dd>{{ summary?.plot.plot_name || '--' }}</dd></div>
          <div><dt>所属区域</dt><dd>{{ summary?.plot.region || '--' }}</dd></div>
          <div><dt>地块面积</dt><dd>{{ plotArea }}</dd></div>
          <div><dt>水稻品种</dt><dd>{{ riceVariety }}</dd></div>
          <div><dt>播种日期</dt><dd>{{ sowingDate }}</dd></div>
          <div><dt>插秧日期</dt><dd>{{ transplantDate }}</dd></div>
          <div><dt>预计成熟期</dt><dd>{{ maturityDate }}</dd></div>
          <div><dt>数据来源</dt><dd>{{ latestDataSource }}</dd></div>
          <div><dt>观测批次</dt><dd>{{ latestBatchId }}</dd></div>
          <div><dt>创建时间</dt><dd>{{ createdAt }}</dd></div>
        </dl>
      </aside>

      <section class="plot-metrics">
        <header class="plot-metrics__header">
          <h3 class="section-title">指标快照</h3>
          <span class="section-subtitle">{{ latestDate }} 观测数据</span>
        </header>
        <EmptyState v-if="!loading && metricSnapshots.length === 0" compact description="当前地块暂无指标数据" />
        <div v-else class="metric-grid">
          <article
            v-for="item in metricSnapshots"
            :key="item.metric_code"
            class="metric-snap"
            :class="`metric-snap--${item.level}`"
          >
            <header>
              <span class="metric-snap__name">{{ item.metric_name }}</span>
              <StatusTag :status="item.quality_flag" />
            </header>
            <div class="metric-snap__value">
              <strong>{{ formatMetricValue(item.value) }}</strong>
              <small v-if="item.value !== null && item.value !== undefined">{{ item.unit }}</small>
            </div>
            <div class="metric-snap__change" :class="item.changeClass">
              <RiseOutlined v-if="item.direction === 'up'" />
              <FallOutlined v-if="item.direction === 'down'" />
              <MinusOutlined v-if="item.direction === 'flat'" />
              <span>{{ item.changeText }}</span>
            </div>
          </article>
        </div>
      </section>

      <section class="plot-trend panel">
        <header class="plot-trend__header">
          <h3 class="section-title">指标趋势</h3>
          <a-select
            v-model:value="selectedTrendMetric"
            :options="trendMetricOptions"
            placeholder="选择指标"
            size="small"
            style="width: 140px"
          />
        </header>
        <div class="plot-trend__range">
          <a-segmented v-model:value="trendRange" :options="trendRangeOptions" size="small" />
        </div>
        <EmptyState v-if="!loading && trendPoints.length === 0" compact description="暂无趋势数据" />
        <EChartView v-else :option="trendOption" :height="280" />
      </section>
    </div>

    <div class="plot-bottom-grid">
      <DataTable
        title="观测批次记录"
        description="当前地块最近的观测批次与数据质量情况。"
        :columns="batchColumns"
        :data-source="batchRows"
        :loading="loading"
        row-key="id"
        :pagination="{ pageSize: 6 }"
        empty-text="当前地块暂无观测记录"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'quality_flag'">
            <StatusTag :status="record.quality_flag as string" />
          </template>
          <template v-if="column.key === 'data_source_id'">
            {{ sourceLabel(record.data_source_id as string | null | undefined) }}
          </template>
        </template>
      </DataTable>

      <section class="warnings-panel panel">
        <header class="warnings-panel__header">
          <h3 class="section-title">预警与建议</h3>
          <RouterLink to="/warnings" class="rf-action-link">查看全部</RouterLink>
        </header>
        <EmptyState v-if="plotWarnings.length === 0" compact description="当前地块暂无预警" />
        <ul v-else class="warnings-list">
          <li v-for="item in plotWarnings.slice(0, 5)" :key="item.warning_id">
            <StatusTag :status="item.warning_type" />
            <div class="warnings-list__body">
              <strong>{{ item.metric_name }}</strong>
              <span>{{ item.message }}</span>
            </div>
            <small>{{ item.observed_at }}</small>
          </li>
        </ul>
        <div class="suggestions">
          <h4>建议措施</h4>
          <ul>
            <li v-for="suggestion in suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </div>
      </section>

      <section class="plot-note-panel panel">
        <h3 class="section-title">地块备注</h3>
        <div class="plot-note-panel__empty">
          <span>暂无备注信息</span>
          <small>当前仅展示备注占位，不保存到后端。</small>
        </div>
      </section>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  AimOutlined,
  EnvironmentOutlined,
  FallOutlined,
  MinusOutlined,
  RiseOutlined,
  RollbackOutlined,
} from '@ant-design/icons-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import {
  fetchMetrics,
  fetchPlots,
  fetchPlotSeries,
  fetchPlotSummary,
  fetchWarnings,
  getApiErrorMessage,
} from '@/api';
import {
  DataTable,
  EChartView,
  EmptyState,
  ErrorState,
  PageContainer,
  StatusTag,
} from '@/components/base';
import {
  buildMapTwinLocation,
  buildPlotDetailRequestPlan,
  shouldReloadPlotDetail,
} from '@/services/pageLinkage';
import { mapQualityToStatus, type StatusLevel } from '@/utils/status';
import type { TableColumnsType } from '@/types/table';
import type {
  Metric,
  MetricSeries,
  Plot,
  PlotSeriesResponse,
  PlotSummaryResponse,
  WarningItem,
} from '@/types/api';

interface MetricSnap {
  metric_code: string;
  metric_name: string;
  value: number | string | null;
  unit: string;
  quality_flag: string;
  level: StatusLevel;
  direction: 'up' | 'down' | 'flat';
  changeText: string;
  changeClass: string;
}

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref('');
const plotNotFound = ref(false);
const selectedPlotId = ref(String(route.params.plotId ?? ''));
const plots = ref<Plot[]>([]);
const metrics = ref<Metric[]>([]);
const summary = ref<PlotSummaryResponse>();
const series = ref<PlotSeriesResponse>();
const allWarnings = ref<WarningItem[]>([]);
const selectedTrendMetric = ref<string>('');
const trendRange = ref<string>('30');
const trendRangeOptions = [
  { label: '近7天', value: '7' },
  { label: '近15天', value: '15' },
  { label: '近30天', value: '30' },
  { label: '全部', value: 'all' },
];

const metricDisplayNames: Record<string, string> = {
  soluble_total_salt: '盐分',
  leaf_area_index: 'LAI',
};

const requiredMetricOrder = [
  'crop_growth',
  'chlorophyll',
  'nitrogen',
  'phosphorus',
  'potassium',
  'ph',
  'organic_matter',
  'soluble_total_salt',
  'leaf_area_index',
  'plant_height',
  'maturity_prediction',
];

const pageTitle = computed(() => `地块画像 / ${summary.value?.plot.plot_code ?? selectedPlotCode.value ?? '--'}`);
const selectedPlotCode = computed(() => plots.value.find((plot) => plot.plot_id === selectedPlotId.value)?.plot_code);
const mapTwinLocation = computed(() => buildMapTwinLocation(selectedPlotId.value));

const plotArea = computed(() => {
  const area = summary.value?.plot ? calculatePolygonAreaMu(summary.value.plot) : undefined;
  return area ? `约 ${area.toFixed(1)} 亩` : '--';
});

const riceVariety = computed(() => '南粳 9108（模拟）');
const sowingDate = computed(() => '2025-03-20（模拟）');
const transplantDate = computed(() => '2025-04-05（模拟）');
const maturityDate = computed(() => '2025-07-28（模拟）');
const createdAt = computed(() => summary.value?.plot.plot_id ? '2025-07-15（模拟）' : '--');

const latestObservation = computed(() =>
  [...(summary.value?.latest_observations ?? [])].sort((a, b) => b.observed_at.localeCompare(a.observed_at))[0],
);
const latestDate = computed(() => latestObservation.value?.observed_at ?? '--');
const latestBatchId = computed(() => latestObservation.value?.batch_id ?? summary.value?.batch_ids[0] ?? '--');
const latestDataSource = computed(() => sourceLabel(latestObservation.value?.data_source_id));

const summaryFacts = computed(() => [
  { label: '地块面积', value: plotArea.value },
  { label: '水稻品种', value: riceVariety.value },
  { label: '最近观测', value: latestDate.value },
  { label: '数据来源', value: latestDataSource.value },
  { label: '观测批次', value: latestBatchId.value },
]);

const plotOverallStatus = computed(() => {
  const counts = summary.value?.quality_counts ?? {};
  if (counts.error || counts.critical) return 'critical';
  if (counts.outlier || counts.abnormal) return 'warning';
  if (counts.missing) return 'missing';
  return 'normal';
});

const metricSnapshots = computed<MetricSnap[]>(() => {
  const observations = summary.value?.latest_observations ?? [];
  const seriesData = series.value?.series ?? [];
  const metricMap = new Map(metrics.value.map((metric) => [metric.metric_code, metric]));
  const orderedMetricCodes = [
    ...requiredMetricOrder.filter((metricCode) => metricMap.has(metricCode)),
    ...metrics.value
      .map((metric) => metric.metric_code)
      .filter((metricCode) => !requiredMetricOrder.includes(metricCode)),
  ];

  return orderedMetricCodes.map((metricCode) => {
    const metricDef = metricMap.get(metricCode);
    const obs = observations.find((item) => item.metric_code === metricCode);
    const metricSeries = seriesData.find((s) => s.metric_code === metricCode);
    const points = [...(metricSeries?.points ?? [])].sort((a, b) => a.observed_at.localeCompare(b.observed_at));
    const currentObservedAt = obs?.observed_at ?? points[points.length - 1]?.observed_at;
    const lastIdx = currentObservedAt ? points.findIndex((p) => p.observed_at === currentObservedAt) : -1;
    const prevPoint = lastIdx > 0 ? points[lastIdx - 1] : undefined;

    let direction: 'up' | 'down' | 'flat' = 'flat';
    let changeText = obs ? '持平' : '暂无数据';
    let changeClass = 'change--flat';

    if (obs && prevPoint && typeof obs.value === 'number' && typeof prevPoint.value === 'number') {
      const diff = obs.value - prevPoint.value;
      if (Math.abs(diff) > 0.01) {
        direction = diff > 0 ? 'up' : 'down';
        const pct = prevPoint.value !== 0 ? Math.abs((diff / prevPoint.value) * 100).toFixed(1) : '--';
        changeText = `${direction === 'up' ? '+' : '-'}${pct}%`;
        changeClass = direction === 'up' ? 'change--up' : 'change--down';
      }
    }

    return {
      metric_code: metricCode,
      metric_name: metricDisplayNames[metricCode] ?? obs?.metric_name ?? metricDef?.metric_name ?? metricCode,
      value: obs?.value ?? null,
      unit: obs?.unit ?? metricDef?.unit ?? '',
      quality_flag: obs?.quality_flag ?? 'empty',
      level: mapQualityToStatus(obs?.quality_flag ?? 'empty'),
      direction,
      changeText,
      changeClass,
    };
  });
});

const trendMetricOptions = computed(() =>
  metricSnapshots.value.map((item) => ({
    label: `${item.metric_name}${item.unit ? ` (${item.unit})` : ''}`,
    value: item.metric_code,
  })),
);

const activeSeries = computed<MetricSeries | undefined>(() =>
  series.value?.series.find((s) => s.metric_code === selectedTrendMetric.value),
);

const trendPoints = computed(() => {
  const points = [...(activeSeries.value?.points ?? [])].sort((a, b) => a.observed_at.localeCompare(b.observed_at));
  if (trendRange.value === 'all') return points;
  const days = parseInt(trendRange.value, 10);
  if (!days || points.length === 0) return points;
  const latestPointDate = points[points.length - 1].observed_at;
  const cutoff = new Date(`${latestPointDate}T00:00:00`);
  cutoff.setDate(cutoff.getDate() - days + 1);
  const cutoffStr = cutoff.toISOString().slice(0, 10);
  return points.filter((p) => p.observed_at >= cutoffStr);
});

const trendOption = computed<EChartsOption>(() => {
  const metric = activeSeries.value;
  const metricDef = metrics.value.find((m) => m.metric_code === selectedTrendMetric.value);
  const normalRange = metricDef?.normal_range;

  const markArea = (normalRange?.min != null && normalRange?.max != null)
    ? { data: [[{ yAxis: normalRange.min }, { yAxis: normalRange.max }] as [{ yAxis: number }, { yAxis: number }]], itemStyle: { color: 'rgba(22, 163, 106, 0.06)' }, silent: true }
    : undefined;

  return {
    tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#edf2ef', textStyle: { color: '#1f2937' } },
    grid: { top: 32, right: 24, bottom: 36, left: 48 },
    xAxis: {
      type: 'category',
      data: trendPoints.value.map((p) => p.observed_at),
      boundaryGap: false,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#6b7280' },
    },
    yAxis: {
      type: 'value',
      name: metric?.unit ?? '',
      nameTextStyle: { color: '#9ca3af' },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#edf2ef' } },
      axisLabel: { color: '#9ca3af' },
    },
    series: [{
      name: metric?.metric_name ?? '指标',
      type: 'line',
      smooth: true,
      symbolSize: 6,
      lineStyle: { width: 2.5, color: '#15905d' },
      itemStyle: { color: '#15905d' },
      areaStyle: { color: 'rgba(21, 144, 93, 0.10)' },
      data: trendPoints.value.map((p) => toNumber(p.value)),
      markArea,
    }],
  };
});

const plotWarnings = computed(() =>
  allWarnings.value.filter((w) => w.plot_id === selectedPlotId.value).slice(0, 5),
);

const suggestions = computed(() => {
  const base = ['建议复核田间观测情况', '建议结合灌溉、施肥和管理措施判断', '建议持续关注后续变化'];
  if (plotWarnings.value.length === 0) return ['当前地块状态正常，建议保持常规观测频率。'];
  return base;
});

const batchRows = computed(() => {
  const points = (series.value?.series ?? []).flatMap((item) => item.points);
  const batchMap = new Map<string, {
    batch_id: string;
    observed_at: string;
    data_source_id: string;
    metric_count: number;
    quality_flag: string;
    remark: string;
  }>();
  for (const point of points) {
    const key = `${point.batch_id}-${point.observed_at}`;
    const existing = batchMap.get(key);
    if (existing) {
      existing.metric_count++;
      existing.quality_flag = mergeQualityFlag(existing.quality_flag, point.quality_flag);
    } else {
      batchMap.set(key, {
        batch_id: point.batch_id,
        observed_at: point.observed_at,
        data_source_id: point.data_source_id,
        metric_count: 1,
        quality_flag: point.quality_flag,
        remark: point.quality_flag === 'normal' ? '--' : qualityRemark(point.quality_flag),
      });
    }
  }
  return [...batchMap.values()]
    .sort((a, b) => b.observed_at.localeCompare(a.observed_at))
    .slice(0, 8)
    .map((item) => ({
      ...item,
      remark: item.quality_flag === 'normal' ? '--' : qualityRemark(item.quality_flag),
      id: `${item.batch_id}-${item.observed_at}`,
    }));
});

const batchColumns: TableColumnsType = [
  { title: '批次编号', dataIndex: 'batch_id', key: 'batch_id', ellipsis: true },
  { title: '观测日期', dataIndex: 'observed_at', key: 'observed_at', width: 110 },
  { title: '数据来源', dataIndex: 'data_source_id', key: 'data_source_id', ellipsis: true },
  { title: '观测指标数', dataIndex: 'metric_count', key: 'metric_count', width: 100 },
  { title: '数据质量', dataIndex: 'quality_flag', key: 'quality_flag', width: 90 },
  { title: '备注', dataIndex: 'remark', key: 'remark', ellipsis: true },
];

onMounted(async () => {
  await initialize();
});

watch(
  () => route.params.plotId,
  async (plotId) => {
    if (shouldReloadPlotDetail(selectedPlotId.value, plotId)) {
      selectedPlotId.value = Array.isArray(plotId) ? plotId[0] : String(plotId);
      await loadPlot();
    }
  },
);

async function initialize() {
  loading.value = true;
  error.value = '';
  try {
    const [plotData, metricData, warningData] = await Promise.all([
      fetchPlots(),
      fetchMetrics(),
      fetchWarnings(),
    ]);
    plots.value = plotData.items;
    metrics.value = metricData.items;
    allWarnings.value = warningData.items;
    selectedPlotId.value = selectedPlotId.value || plotData.items[0]?.plot_id || '';
    await loadPlot();
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地块画像基础数据加载失败。');
  } finally {
    loading.value = false;
  }
}

async function loadPlot() {
  const requestPlan = buildPlotDetailRequestPlan(selectedPlotId.value);
  if (!requestPlan) return;
  loading.value = true;
  error.value = '';
  plotNotFound.value = false;
  try {
    const [summaryData, seriesData] = await Promise.all([
      fetchPlotSummary(requestPlan.summaryPlotId),
      fetchPlotSeries(requestPlan.seriesFilters),
    ]);
    summary.value = summaryData;
    series.value = seriesData;
    const nextMetric = seriesData.series.find((item) => item.metric_code === 'chlorophyll') ?? seriesData.series[0];
    if (!selectedTrendMetric.value && nextMetric) {
      selectedTrendMetric.value = nextMetric.metric_code;
    }
  } catch (currentError) {
    summary.value = undefined;
    series.value = undefined;
    const message = getApiErrorMessage(currentError, '地块画像加载失败。');
    error.value = message;
    plotNotFound.value = message.includes('未找到地块');
  } finally {
    loading.value = false;
  }
}

function formatValue(value: number | string | null): string {
  if (value === null || value === undefined || value === '') return '--';
  if (typeof value === 'number') return value.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
  return value;
}

function formatMetricValue(value: number | string | null): string {
  if (value === null || value === undefined || value === '') return '暂无数据';
  return formatValue(value);
}

function toNumber(value: number | string | null): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

function sourceLabel(value?: string | null) {
  if (!value) return '--';
  if (value.includes('simulated') || value.includes('demo')) return '模拟数据';
  if (value.includes('generated')) return '程序生成';
  return value;
}

function mergeQualityFlag(current: string, next: string) {
  const order: Record<string, number> = { normal: 0, missing: 1, outlier: 2, error: 3 };
  return (order[next] ?? 0) > (order[current] ?? 0) ? next : current;
}

function qualityRemark(flag: string) {
  if (flag === 'missing') return '存在缺失指标';
  if (flag === 'outlier' || flag === 'abnormal') return '存在异常指标';
  if (flag === 'error' || flag === 'critical') return '存在严重质量问题';
  return '--';
}

function returnToMap() {
  void router.push('/map-twin');
}

function calculatePolygonAreaMu(plot: Plot) {
  if (plot.geometry?.type !== 'Polygon' || !Array.isArray(plot.geometry.coordinates)) {
    return undefined;
  }
  const ring = plot.geometry.coordinates[0];
  if (!Array.isArray(ring) || ring.length < 4) {
    return undefined;
  }

  const points = ring
    .filter((point): point is [number, number] =>
      Array.isArray(point) && typeof point[0] === 'number' && typeof point[1] === 'number',
    );
  if (points.length < 4) {
    return undefined;
  }

  const avgLat = points.reduce((sum, [, lat]) => sum + lat, 0) / points.length;
  const metersPerDegreeLat = 111_320;
  const metersPerDegreeLng = 111_320 * Math.cos((avgLat * Math.PI) / 180);
  const projected = points.map(([lng, lat]) => [lng * metersPerDegreeLng, lat * metersPerDegreeLat]);
  let area = 0;
  for (let index = 0; index < projected.length; index += 1) {
    const [x1, y1] = projected[index];
    const [x2, y2] = projected[(index + 1) % projected.length];
    area += x1 * y2 - x2 * y1;
  }
  return Math.abs(area) / 2 / 666.667;
}
</script>

<style scoped>
.plot-empty {
  display: grid;
  justify-items: center;
  gap: 16px;
  padding: 36px 24px;
}

.plot-summary {
  display: grid;
  grid-template-columns: minmax(220px, 0.72fr) minmax(0, 2fr) auto;
  align-items: center;
  gap: 24px;
  padding: 24px 28px;
}

.plot-summary__identity {
  min-width: 0;
}

.plot-summary__id {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.plot-summary__id strong {
  font-size: 28px;
  font-weight: 800;
  color: var(--rf-primary);
}

.plot-summary h2 {
  margin: 0 0 8px;
  color: var(--rf-text);
  font-size: 18px;
  font-weight: 700;
}

.plot-summary__region {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--rf-text-muted);
  font-size: 13px;
}

.plot-summary__region :deep(svg) {
  color: var(--rf-text-soft);
}

.plot-summary__facts {
  display: grid;
  grid-template-columns: repeat(5, minmax(108px, 1fr));
  min-width: 0;
}

.plot-summary__fact {
  min-width: 0;
  border-left: 1px solid var(--rf-border-soft);
  padding: 4px 14px;
}

.plot-summary__fact span {
  display: block;
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.4;
}

.plot-summary__fact strong {
  display: -webkit-box;
  margin-top: 8px;
  color: var(--rf-text);
  font-size: 16px;
  font-weight: 800;
  line-height: 1.25;
  overflow: hidden;
  overflow-wrap: anywhere;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.plot-summary__actions {
  justify-self: end;
}

.plot-body {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) minmax(320px, 0.42fr);
  gap: 16px;
}

.plot-info {
  padding: 18px 16px;
}

.plot-info h3 {
  margin-bottom: 14px;
}

.info-list {
  display: grid;
  gap: 10px;
  margin: 0;
}

.info-list div {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
  border-bottom: 1px solid var(--rf-border-soft);
  padding-bottom: 8px;
}

.info-list div:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.info-list dt {
  color: var(--rf-text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.info-list dd {
  margin: 0;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 600;
  text-align: right;
  overflow-wrap: anywhere;
}

.plot-notes {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid var(--rf-border-soft);
}

.plot-notes h4 {
  margin: 0 0 8px;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.plot-notes p {
  margin: 0;
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.6;
}

.plot-metrics {
  min-width: 0;
}

.plot-metrics__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.metric-snap {
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: var(--rf-surface);
  box-shadow: var(--rf-shadow-soft);
  padding: 14px 16px;
  transition: border-color 0.15s ease;
}

.metric-snap:hover {
  border-color: var(--rf-border);
}

.metric-snap header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.metric-snap__name {
  color: var(--rf-text-muted);
  font-size: 12px;
  font-weight: 600;
}

.metric-snap__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 6px;
}

.metric-snap__value strong {
  color: var(--rf-text);
  font-size: 22px;
  font-weight: 800;
  line-height: 1.1;
}

.metric-snap__value small {
  color: var(--rf-text-soft);
  font-size: 12px;
}

.metric-snap__change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.change--up {
  color: var(--rf-status-normal);
}

.change--down {
  color: var(--rf-status-critical);
}

.change--flat {
  color: var(--rf-text-soft);
}

.metric-snap--normal {
  border-left: 3px solid var(--rf-status-normal);
}

.metric-snap--watch {
  border-left: 3px solid var(--rf-status-watch);
}

.metric-snap--warning {
  border-left: 3px solid var(--rf-status-warning);
}

.metric-snap--critical {
  border-left: 3px solid var(--rf-status-critical);
}

.metric-snap--empty {
  border-left: 3px solid var(--rf-status-empty);
}

.plot-trend {
  padding: 18px 16px;
}

.plot-trend__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.plot-trend__range {
  margin-bottom: 14px;
}

.plot-bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.9fr) minmax(260px, 0.65fr);
  gap: 16px;
  align-items: stretch;
}

.warnings-panel {
  padding: 18px 20px;
}

.warnings-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}

.warnings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0 0 16px;
  padding: 0;
  list-style: none;
}

.warnings-list li {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
}

.warnings-list__body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.warnings-list__body strong {
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.warnings-list__body span {
  color: var(--rf-text-muted);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.warnings-list li small {
  color: var(--rf-text-soft);
  font-size: 11px;
  white-space: nowrap;
}

.suggestions {
  border-top: 1px solid var(--rf-border-soft);
  padding-top: 14px;
}

.suggestions h4 {
  margin: 0 0 8px;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.suggestions ul {
  margin: 0;
  padding: 0 0 0 18px;
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.8;
}

.plot-note-panel {
  display: flex;
  min-height: 260px;
  flex-direction: column;
  padding: 18px 20px;
}

.plot-note-panel__empty {
  display: grid;
  flex: 1;
  place-items: center;
  align-content: center;
  gap: 8px;
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius);
  background: var(--rf-surface-soft);
  color: var(--rf-text-muted);
  text-align: center;
}

.plot-note-panel__empty span {
  font-size: 13px;
  font-weight: 700;
}

.plot-note-panel__empty small {
  max-width: 220px;
  color: var(--rf-text-soft);
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 1180px) {
  .plot-summary,
  .plot-body {
    grid-template-columns: 1fr;
  }

  .plot-summary__facts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .plot-summary__fact {
    border-left: 0;
    border-top: 1px solid var(--rf-border-soft);
    padding: 12px 0 0;
  }

  .plot-summary__actions {
    justify-self: start;
  }
}

@media (max-width: 1380px) {
  .plot-bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 920px) {
  .plot-summary__facts {
    grid-template-columns: 1fr;
  }
}
</style>
