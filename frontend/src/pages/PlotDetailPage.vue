<template>
  <PageContainer
    :title="`地块 ${summary?.plot.plot_code || selectedPlotId || '--'}`"
    description="查看单个地块的基础信息、地图定位、多指标趋势和数据来源追溯。"
    breadcrumb="地块详情"
  >
    <FilterBar>
      <a-select
        v-model:value="selectedPlotId"
        :options="plotOptions"
        show-search
        option-filter-prop="label"
        placeholder="选择地块"
        @change="handlePlotChange"
      />
      <a-select
        v-model:value="selectedMetricCodes"
        mode="multiple"
        :options="metricOptions"
        :max-tag-count="3"
        placeholder="选择趋势指标"
        option-filter-prop="label"
      />
      <a-button type="primary" :loading="loading" @click="loadPlot">刷新详情</a-button>
      <a-button @click="$router.push('/map-twin')">返回地图</a-button>
    </FilterBar>

    <ErrorState v-if="error" :message="error" compact />

    <div class="page-grid page-grid--four">
      <StatCard label="所属区域" :value="summary?.plot.region || '--'" :icon="EnvironmentOutlined" />
      <StatCard label="地块状态" :value="summary?.plot.status || '--'" tone="green" :icon="SafetyCertificateOutlined" />
      <StatCard label="最近观测日期" :value="latestObservation?.observed_at || '--'" tone="cyan" :icon="CalendarOutlined" />
      <StatCard label="观测批次" :value="summary?.batch_ids[0] || '--'" tone="purple" :icon="DatabaseOutlined" />
    </div>

    <div class="plot-layout">
      <section class="panel plot-info">
        <h2 class="section-title">地块基础信息</h2>
        <EmptyState v-if="!summary?.plot && !loading" compact description="暂无地块基础信息" />
        <dl v-else class="plot-info__list">
          <div>
            <dt>地块编号</dt>
            <dd>{{ summary?.plot.plot_code || '--' }}</dd>
          </div>
          <div>
            <dt>地块名称</dt>
            <dd>{{ summary?.plot.plot_name || '--' }}</dd>
          </div>
          <div>
            <dt>地块 ID</dt>
            <dd>{{ summary?.plot.plot_id || selectedPlotId || '--' }}</dd>
          </div>
          <div>
            <dt>别名</dt>
            <dd>{{ summary?.plot.aliases?.join('、') || '--' }}</dd>
          </div>
          <div>
            <dt>数据完整率</dt>
            <dd>{{ completeness }}%</dd>
          </div>
          <div>
            <dt>异常/缺失数</dt>
            <dd>{{ abnormalCount }}</dd>
          </div>
        </dl>
      </section>

      <CesiumMapPanel
        title="地图定位"
        :feature-collection="singlePlotCollection"
        :height="330"
        :loading="loading"
        :selected-plot-id="selectedPlotId"
      />

      <section class="panel key-metrics">
        <div class="key-metrics__header">
          <h2 class="section-title">当前指标快照</h2>
          <span>{{ latestObservation?.observed_at || '暂无日期' }}</span>
        </div>
        <EmptyState v-if="!keyMetrics.length && !loading" compact description="当前地块暂无指标快照" />
        <div v-else class="key-metrics__grid">
          <div v-for="item in keyMetrics" :key="item.metric_code">
            <span>{{ item.metric_name }}</span>
            <MetricValueTag :value="item.value" :unit="item.unit" :quality-flag="item.quality_flag" />
          </div>
        </div>
      </section>
    </div>

    <ChartCard
      title="多指标趋势"
      description="按观测日期展示所选指标的时间变化；非数值型观测不会进入折线图。"
      :loading="loading"
      :empty="trendSeries.length === 0"
      empty-text="当前筛选下暂无可展示的数值型趋势"
      :height="360"
    >
      <EChartView :option="trendOption" :height="360" />
    </ChartCard>

    <div class="page-grid page-grid--two">
      <DataTable
        title="数据来源追溯"
        description="展示最新观测值对应的观测批次、数据来源和质量状态。"
        :columns="traceColumns"
        :data-source="traceRows"
        :loading="loading"
        row-key="id"
        :pagination="{ pageSize: 8 }"
        empty-text="当前地块暂无来源记录"
        :scroll="{ x: 760 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'value'">
            <MetricValueTag
              :value="record.value as number | string | null"
              :unit="record.unit as string"
              :quality-flag="record.quality_flag as string"
            />
          </template>
          <template v-if="column.key === 'quality_flag'">
            <StatusTag :status="record.quality_flag as string" />
          </template>
        </template>
      </DataTable>

      <DataTable
        title="质量状态汇总"
        description="按地块最新观测记录统计质量标记数量。"
        :columns="qualityColumns"
        :data-source="qualityRows"
        :loading="loading"
        row-key="quality_flag"
        empty-text="当前地块暂无质量状态"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'quality_flag'">
            <StatusTag :status="record.quality_flag as string" />
          </template>
        </template>
      </DataTable>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  CalendarOutlined,
  DatabaseOutlined,
  EnvironmentOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons-vue';
import type { TableColumnsType } from 'ant-design-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import {
  fetchMetrics,
  fetchPlots,
  fetchPlotSeries,
  fetchPlotSummary,
  getApiErrorMessage,
} from '@/api';
import {
  CesiumMapPanel,
  ChartCard,
  DataTable,
  EChartView,
  EmptyState,
  ErrorState,
  FilterBar,
  MetricValueTag,
  PageContainer,
  StatCard,
  StatusTag,
} from '@/components/base';
import {
  buildPlotDetailRequestPlan,
  shouldReloadPlotDetail,
} from '@/services/pageLinkage';
import type {
  MapFeatureCollection,
  Metric,
  MetricSeries,
  Plot,
  PlotSeriesPoint,
  PlotSeriesResponse,
  PlotSummaryResponse,
} from '@/types/api';

interface TraceRow {
  id: string;
  metric_code: string;
  metric_name: string;
  value: number | string | null;
  unit: string;
  observed_at: string;
  quality_flag: string;
  batch_id: string;
  data_source_id: string;
}

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref('');
const selectedPlotId = ref(String(route.params.plotId ?? ''));
const selectedMetricCodes = ref<string[]>([]);
const plots = ref<Plot[]>([]);
const metrics = ref<Metric[]>([]);
const summary = ref<PlotSummaryResponse>();
const series = ref<PlotSeriesResponse>();

const plotOptions = computed(() =>
  plots.value.map((plot) => ({ label: `${plot.plot_code}（${plot.region}）`, value: plot.plot_id })),
);
const metricOptions = computed(() =>
  (series.value?.series ?? []).map((item) => ({
    label: `${item.metric_name}${item.unit ? `（${item.unit}）` : ''}`,
    value: item.metric_code,
  })),
);
const latestObservation = computed(() =>
  [...(summary.value?.latest_observations ?? [])].sort((a, b) => b.observed_at.localeCompare(a.observed_at))[0],
);
const keyMetrics = computed(() => (summary.value?.latest_observations ?? []).slice(0, 8));
const abnormalCount = computed(() =>
  (summary.value?.latest_observations ?? []).filter((item) => item.quality_flag !== 'normal').length,
);
const completeness = computed(() => {
  const total = metrics.value.length;
  if (!total) {
    return 0;
  }
  return Math.round(((summary.value?.latest_observations.length ?? 0) / total) * 1000) / 10;
});

const trendSeries = computed(() =>
  (series.value?.series ?? [])
    .filter((item) => selectedMetricCodes.value.includes(item.metric_code))
    .filter((item) => item.points.some((point) => toNumber(point.value) !== null)),
);
const trendOption = computed<EChartsOption>(() => buildTrendOption(trendSeries.value));

const singlePlotCollection = computed<MapFeatureCollection>(() => {
  const plot = summary.value?.plot;
  if (!plot?.geometry) {
    return { type: 'FeatureCollection', features: [] };
  }
  return {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: plot.geometry,
        properties: {
          plot_id: plot.plot_id,
          plot_code: plot.plot_code,
          plot_name: plot.plot_name,
          region: plot.region,
          status: plot.status,
          fill_color: '#16a34a',
          quality_flag: 'normal',
        },
      },
    ],
  };
});

const traceRows = computed<TraceRow[]>(() =>
  (summary.value?.latest_observations ?? []).map((item) => ({
    ...item,
    quality_flag: item.quality_flag,
    id: `${item.metric_code}-${item.observed_at}-${item.batch_id}`,
  })),
);
const qualityRows = computed(() =>
  Object.entries(summary.value?.quality_counts ?? {}).map(([qualityFlag, count]) => ({
    quality_flag: qualityFlag,
    count,
  })),
);

const traceColumns: TableColumnsType = [
  { title: '指标', dataIndex: 'metric_name', key: 'metric_name', width: 140 },
  { title: '当前值', dataIndex: 'value', key: 'value', width: 120 },
  { title: '观测日期', dataIndex: 'observed_at', key: 'observed_at', width: 120 },
  { title: '观测批次', dataIndex: 'batch_id', key: 'batch_id', width: 190 },
  { title: '数据来源', dataIndex: 'data_source_id', key: 'data_source_id', width: 220 },
  { title: '质量状态', dataIndex: 'quality_flag', key: 'quality_flag', width: 110 },
];
const qualityColumns: TableColumnsType = [
  { title: '质量状态', dataIndex: 'quality_flag', key: 'quality_flag' },
  { title: '记录数', dataIndex: 'count', key: 'count' },
];

onMounted(async () => {
  await initialize();
});

watch(
  () => route.params.plotId,
  async (plotId) => {
    if (shouldReloadPlotDetail(selectedPlotId.value, plotId)) {
      const nextPlotId = Array.isArray(plotId) ? plotId[0] : String(plotId);
      selectedPlotId.value = nextPlotId;
      await loadPlot();
    }
  },
);

async function initialize() {
  loading.value = true;
  error.value = '';
  try {
    const [plotData, metricData] = await Promise.all([fetchPlots(), fetchMetrics()]);
    plots.value = plotData.items;
    metrics.value = metricData.items;
    selectedPlotId.value = selectedPlotId.value || plotData.items[0]?.plot_id || '';
    await loadPlot();
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地块详情基础数据加载失败。');
  } finally {
    loading.value = false;
  }
}

async function handlePlotChange() {
  const requestPlan = buildPlotDetailRequestPlan(selectedPlotId.value);
  if (!requestPlan) {
    summary.value = undefined;
    series.value = undefined;
    selectedMetricCodes.value = [];
    return;
  }
  await router.replace(requestPlan.routeLocation);
  await loadPlot();
}

async function loadPlot() {
  const requestPlan = buildPlotDetailRequestPlan(selectedPlotId.value);
  if (!requestPlan) {
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const [summaryData, seriesData] = await Promise.all([
      fetchPlotSummary(requestPlan.summaryPlotId),
      fetchPlotSeries(requestPlan.seriesFilters),
    ]);
    summary.value = summaryData;
    series.value = seriesData;
    const availableCodes = seriesData.series.map((item) => item.metric_code);
    const preservedCodes = selectedMetricCodes.value.filter((code) => availableCodes.includes(code));
    selectedMetricCodes.value = preservedCodes.length ? preservedCodes : availableCodes.slice(0, 4);
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地块详情加载失败。');
  } finally {
    loading.value = false;
  }
}

function buildTrendOption(items: MetricSeries[]): EChartsOption {
  const dates = [...new Set(items.flatMap((item) => item.points.map((point) => point.observed_at)))].sort();
  return {
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        const rows = Array.isArray(params) ? params : [params];
        const firstRow = rows[0] as { axisValue?: string | number; name?: string } | undefined;
        const title = firstRow?.axisValue ?? firstRow?.name ?? '';
        const body = rows.map((row) => {
          const data = row.data as { value: number | null; point?: PlotSeriesPoint };
          const point = data.point;
          const valueText = data.value === null ? '--' : `${data.value}`;
          return [
            `${row.marker}${row.seriesName}: ${valueText}`,
            point ? `质量：${point.quality_flag}` : '',
            point?.data_source_id ? `来源：${point.data_source_id}` : '',
          ].filter(Boolean).join('<br/>');
        }).join('<br/>');
        return `${title}<br/>${body}`;
      },
    },
    legend: { top: 0, type: 'scroll' },
    grid: { top: 46, right: 24, bottom: 36, left: 48 },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f0' } } },
    series: items.map((item) => ({
      name: item.metric_name,
      type: 'line',
      smooth: true,
      symbolSize: 5,
      connectNulls: false,
      data: dates.map((date) => {
        const point = item.points.find((candidate) => candidate.observed_at === date);
        return {
          value: point ? toNumber(point.value) : null,
          point,
        };
      }),
    })),
  };
}

function toNumber(value: number | string | null) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string' && value.trim()) {
    const numericValue = Number(value);
    return Number.isFinite(numericValue) ? numericValue : null;
  }
  return null;
}
</script>

<style scoped>
.plot-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 360px;
  gap: 14px;
}

.plot-info,
.key-metrics {
  padding: 16px;
}

.plot-info__list {
  display: grid;
  gap: 12px;
  margin: 14px 0 0;
}

.plot-info__list div {
  border-bottom: 1px solid var(--rf-border-soft);
  padding-bottom: 10px;
}

.plot-info__list div:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.plot-info__list dt {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.plot-info__list dd {
  margin: 4px 0 0;
  color: var(--rf-text);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.key-metrics__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.key-metrics__header span {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.key-metrics__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.key-metrics__grid div {
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: #f8fbfa;
  padding: 10px;
}

.key-metrics__grid span {
  display: block;
  margin-bottom: 8px;
  color: var(--rf-text-muted);
  font-size: 12px;
}

@media (max-width: 1260px) {
  .plot-layout {
    grid-template-columns: 1fr;
  }
}
</style>
