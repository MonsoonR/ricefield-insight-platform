<template>
  <PageContainer
    title="Cesium 地图孪生"
    description="在 Cesium 卫星底图上展示程序生成地块边界、指标着色、地块点击和趋势联动。"
  >
    <FilterBar>
      <MetricSelector v-model="filters.metricCode" :options="metricOptions" :loading="loading" />
      <DateSelector v-model="filters.observedAt" :dates="dates" :loading="loading" />
      <RegionSelector v-model="filters.region" />
      <a-input v-model:value="plotKeyword" allow-clear placeholder="搜索地块编号" />
      <a-button type="primary" :loading="loading" @click="loadMap">刷新图层</a-button>
    </FilterBar>

    <ErrorState v-if="error" :message="error" compact />

    <div class="map-layout">
      <CesiumMapPanel
        title="地块指标空间分布"
        :feature-collection="filteredFeatureCollection"
        :loading="loading"
        :selected-plot-id="selectedPlotId"
        :height="620"
        @plot-click="handlePlotClick"
        @imagery-error="imageryError = $event"
      >
        <template #toolbar>
          <a-space>
            <a-button @click="selectFirstPlot">定位地块</a-button>
            <a-button @click="clearSelection">清除</a-button>
          </a-space>
        </template>
        <template #legend>
          <div class="map-legend">
            <strong>{{ currentMetricName }}</strong>
            <span><i class="legend-good" />正常</span>
            <span><i class="legend-attention" />关注</span>
            <span><i class="legend-warning" />预警</span>
            <span><i class="legend-error" />严重</span>
            <span><i class="legend-empty" />无数据</span>
          </div>
        </template>
      </CesiumMapPanel>

      <aside class="panel map-detail">
        <div class="map-detail__title">
          <div>
            <h2>地块详情</h2>
            <p>{{ selectedPlotId ? '已选择地块' : '点击地图地块查看详情' }}</p>
          </div>
          <StatusTag :status="selectedProperties?.quality_flag || selectedProperties?.status" />
        </div>

        <EmptyState v-if="!selectedPlotId" compact description="尚未选择地块" />
        <template v-else>
          <div class="map-detail__plot">
            <strong>{{ selectedProperties?.plot_code || selectedPlotId }}</strong>
            <span>{{ selectedProperties?.region || summary?.plot.region || '--' }}</span>
          </div>
          <dl class="map-detail__list">
            <div>
              <dt>当前指标</dt>
              <dd>{{ currentMetricName }}</dd>
            </div>
            <div>
              <dt>当前值</dt>
              <dd><MetricValueTag :value="selectedProperties?.value" :unit="selectedProperties?.unit" :quality-flag="selectedProperties?.quality_flag" /></dd>
            </div>
            <div>
              <dt>观测日期</dt>
              <dd>{{ selectedProperties?.observed_at || filters.observedAt || '--' }}</dd>
            </div>
            <div>
              <dt>观测批次</dt>
              <dd>{{ activeObservation?.batch_id || selectedProperties?.batch_id || '--' }}</dd>
            </div>
            <div>
              <dt>数据来源</dt>
              <dd>{{ activeObservation?.data_source_id || selectedProperties?.data_source_id || '--' }}</dd>
            </div>
          </dl>
          <RouterLink :to="`/plot-detail/${encodeURIComponent(selectedPlotId)}`">
            <a-button block type="primary">查看地块详情</a-button>
          </RouterLink>
        </template>
      </aside>
    </div>

    <div v-if="imageryError" class="placeholder-banner">{{ imageryError }}</div>

    <div class="page-grid page-grid--asymmetric">
      <ChartCard title="当前地块趋势" :loading="seriesLoading" :empty="!selectedSeriesPoints.length" empty-text="选择地块后显示趋势">
        <EChartView :option="plotTrendOption" :height="280" />
      </ChartCard>

      <ChartCard title="当前筛选摘要" :loading="loading">
        <div class="map-summary">
          <div><span>地块数量</span><strong>{{ filteredFeatureCollection.features.length }}</strong></div>
          <div><span>正常状态占比</span><strong>{{ validRate }}%</strong></div>
          <div><span>区域</span><strong>{{ regionLabel }}</strong></div>
          <div><span>日期</span><strong>{{ filters.observedAt || '最新' }}</strong></div>
        </div>
      </ChartCard>
    </div>

    <DataTable
      title="关键指标表"
      :columns="metricColumns"
      :data-source="summaryRows"
      :loading="seriesLoading"
      row-key="metric_code"
      empty-text="选择地块后查看关键指标"
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
  </PageContainer>
</template>

<script setup lang="ts">
import type { TableColumnsType } from 'ant-design-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref, watch } from 'vue';

import {
  fetchDates,
  fetchMapLayers,
  fetchMetrics,
  fetchPlotSeries,
  fetchPlotSummary,
  getApiErrorMessage,
} from '@/api';
import {
  CesiumMapPanel,
  ChartCard,
  DataTable,
  DateSelector,
  EChartView,
  EmptyState,
  ErrorState,
  FilterBar,
  MetricSelector,
  MetricValueTag,
  PageContainer,
  RegionSelector,
  StatusTag,
} from '@/components/base';
import type {
  MapFeatureCollection,
  MapFeatureProperties,
  Metric,
  MetricSeries,
  PlotMetricSnapshot,
  PlotSeriesResponse,
  PlotSummaryResponse,
  RegionCode,
} from '@/types/api';

const emptyCollection: MapFeatureCollection = { type: 'FeatureCollection', features: [] };

const loading = ref(false);
const seriesLoading = ref(false);
const error = ref('');
const imageryError = ref('');
const metrics = ref<Metric[]>([]);
const dates = ref<string[]>([]);
const featureCollection = ref<MapFeatureCollection>(emptyCollection);
const selectedPlotId = ref('');
const selectedProperties = ref<MapFeatureProperties>();
const summary = ref<PlotSummaryResponse>();
const series = ref<PlotSeriesResponse>();
const plotKeyword = ref('');

const filters = reactive<{
  region: RegionCode;
  metricCode?: string;
  observedAt?: string;
}>({
  region: 'all',
  metricCode: undefined,
  observedAt: undefined,
});

const metricOptions = computed(() =>
  metrics.value.map((metric) => ({
    label: metric.metric_name,
    value: metric.metric_code,
    unit: metric.unit,
  })),
);
const currentMetric = computed(() => metrics.value.find((item) => item.metric_code === filters.metricCode));
const currentMetricName = computed(() => currentMetric.value?.metric_name ?? '指标');
const regionLabel = computed(() => ({ all: '全部区域', east: '试验一区', west: '试验二区' }[filters.region]));

const filteredFeatureCollection = computed<MapFeatureCollection>(() => {
  if (!plotKeyword.value.trim()) {
    return featureCollection.value;
  }
  const keyword = plotKeyword.value.trim().toLowerCase();
  return {
    type: 'FeatureCollection',
    features: featureCollection.value.features.filter((feature) =>
      [feature.properties.plot_id, feature.properties.plot_code, feature.properties.plot_name]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(keyword)),
    ),
  };
});

const activeObservation = computed(() =>
  summary.value?.latest_observations.find((item) => item.metric_code === filters.metricCode),
);
const activeSeries = computed<MetricSeries | undefined>(() =>
  series.value?.series.find((item) => item.metric_code === filters.metricCode) ?? series.value?.series[0],
);
const selectedSeriesPoints = computed(() =>
  [...(activeSeries.value?.points ?? [])].sort((a, b) => a.observed_at.localeCompare(b.observed_at)),
);
const validRate = computed(() => {
  const features = filteredFeatureCollection.value.features;
  if (!features.length) {
    return 0;
  }
  const valid = features.filter((feature) =>
    !feature.properties.quality_flag || feature.properties.quality_flag === 'normal',
  ).length;
  return Math.round((valid / features.length) * 1000) / 10;
});

const plotTrendOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 24, right: 18, bottom: 28, left: 42 },
  xAxis: { type: 'category', data: selectedSeriesPoints.value.map((point) => point.observed_at), boundaryGap: false },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f0' } } },
  series: [{
    name: activeSeries.value?.metric_name ?? currentMetricName.value,
    type: 'line',
    smooth: true,
    symbolSize: 7,
    data: selectedSeriesPoints.value.map((point) => point.value),
    lineStyle: { width: 3, color: '#15905d' },
    itemStyle: { color: '#15905d' },
    areaStyle: { color: 'rgba(7, 136, 63, 0.10)' },
  }],
}));

const summaryRows = computed(() =>
  (summary.value?.latest_observations ?? []).map((item) => ({
    ...item,
    id: `${item.metric_code}-${item.observed_at}`,
  })),
);

const metricColumns: TableColumnsType = [
  { title: '指标', dataIndex: 'metric_name', key: 'metric_name' },
  { title: '当前值', dataIndex: 'value', key: 'value' },
  { title: '观测日期', dataIndex: 'observed_at', key: 'observed_at' },
  { title: '质量状态', dataIndex: 'quality_flag', key: 'quality_flag' },
  { title: '观测批次', dataIndex: 'batch_id', key: 'batch_id' },
  { title: '数据来源', dataIndex: 'data_source_id', key: 'data_source_id' },
];

onMounted(() => {
  void initialize();
});

watch(
  () => [filters.region, filters.metricCode, filters.observedAt],
  () => {
    void loadMap();
  },
);

async function initialize() {
  loading.value = true;
  try {
    const [metricData, dateData] = await Promise.all([fetchMetrics(), fetchDates()]);
    metrics.value = metricData.items;
    dates.value = dateData.items;
    filters.metricCode = metricData.items[0]?.metric_code;
    filters.observedAt = dateData.items[dateData.items.length - 1];
    await loadMap();
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地图筛选数据加载失败。');
  } finally {
    loading.value = false;
  }
}

async function loadMap() {
  if (!filters.metricCode) {
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const response = await fetchMapLayers({
      region: filters.region,
      metricCode: filters.metricCode,
      observedAt: filters.observedAt,
    });
    featureCollection.value = response.layers[0]?.feature_collection ?? emptyCollection;
    if (selectedPlotId.value) {
      const next = featureCollection.value.features.find((feature) => feature.properties.plot_id === selectedPlotId.value);
      selectedProperties.value = next?.properties;
      await loadSelectedPlot();
    }
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地图图层加载失败，请检查 /api/map/layers。');
  } finally {
    loading.value = false;
  }
}

async function handlePlotClick(properties: MapFeatureProperties) {
  if (!properties.plot_id) {
    return;
  }
  selectedPlotId.value = properties.plot_id;
  selectedProperties.value = properties;
  await loadSelectedPlot();
}

async function loadSelectedPlot() {
  if (!selectedPlotId.value) {
    return;
  }
  seriesLoading.value = true;
  try {
    const [summaryData, seriesData] = await Promise.all([
      fetchPlotSummary(selectedPlotId.value),
      fetchPlotSeries({ plotId: selectedPlotId.value, metricCode: filters.metricCode }),
    ]);
    summary.value = summaryData;
    series.value = seriesData;
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地块详情或趋势加载失败。');
  } finally {
    seriesLoading.value = false;
  }
}

function selectFirstPlot() {
  const first = filteredFeatureCollection.value.features[0]?.properties;
  if (first?.plot_id) {
    void handlePlotClick(first);
  }
}

function clearSelection() {
  selectedPlotId.value = '';
  selectedProperties.value = undefined;
  summary.value = undefined;
  series.value = undefined;
}
</script>

<style scoped>
.map-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
}

.map-detail {
  padding: 20px;
}

.map-detail__title,
.map-detail__plot {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.map-detail__title h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 850;
}

.map-detail__title p,
.map-detail__plot span {
  margin: 4px 0 0;
  color: var(--rf-text-muted);
  font-size: 13px;
}

.map-detail__plot {
  align-items: center;
  border-top: 1px solid var(--rf-border-soft);
  margin-top: 14px;
  padding-top: 16px;
}

.map-detail__plot strong {
  color: var(--rf-text);
  font-size: 32px;
  font-weight: 900;
}

.map-detail__list {
  display: grid;
  gap: 11px;
  margin: 16px 0;
}

.map-detail__list div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--rf-border-soft);
  padding-bottom: 10px;
}

.map-detail__list div:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.map-detail__list dt {
  color: var(--rf-text-muted);
}

.map-detail__list dd {
  margin: 0;
  text-align: right;
  font-weight: 750;
}

.map-legend {
  display: grid;
  gap: 8px;
  min-width: 160px;
}

.map-legend strong,
.map-legend span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 12px;
}

.map-legend i {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

.legend-good {
  background: #16a34a;
}

.legend-warning {
  background: #f97316;
}

.legend-attention {
  background: #f6c343;
}

.legend-error {
  background: #ef3b2d;
}

.legend-empty {
  background: #d1d5db;
}

.map-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.map-summary div {
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: #f8fbfa;
  padding: 14px;
}

.map-summary span,
.map-summary strong {
  display: block;
}

.map-summary span {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.map-summary strong {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 900;
}

@media (max-width: 1180px) {
  .map-layout {
    grid-template-columns: 1fr;
  }
}
</style>
