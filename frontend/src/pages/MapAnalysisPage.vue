<template>
  <PageContainer>
    <ErrorState v-if="error" :message="error" compact />

    <div class="map-workbench">
      <div class="map-workbench__main">
        <CesiumMapPanel
          :feature-collection="filteredFeatureCollection"
          :loading="loading"
          :selected-plot-id="selectedPlotId"
          :height="620"
          :show-boundaries="layerToggles.boundaries"
          :show-metric-layer="layerToggles.metric"
          :show-warnings="layerToggles.warnings"
          :show-region-boundary="layerToggles.region"
          @plot-click="handlePlotClick"
          @imagery-error="imageryError = $event"
        >
          <template #filters>
            <FilterBar class="map-filter-bar">
              <MetricSelector v-model="filters.metricCode" :options="metricOptions" :loading="loading" />
              <DateSelector v-model="filters.observedAt" :dates="dates" :loading="loading" />
              <RegionSelector v-model="filters.region" />
              <a-button type="primary" :loading="loading" @click="loadMap">查询</a-button>
              <a-button @click="resetFilters">重置</a-button>
            </FilterBar>
          </template>
          <template #legend>
            <div class="map-legend">
              <strong>{{ currentMetricName }}{{ currentMetric?.unit ? `（${currentMetric.unit}）` : '' }}</strong>
              <div class="map-legend__scale">
                <span>低值</span>
                <i />
                <span>高值</span>
              </div>
              <span><b class="legend-empty" />无数据</span>
              <span><b class="legend-boundary" />地块边界</span>
              <span><b class="legend-warning" />预警 / 严重</span>
            </div>
          </template>
        </CesiumMapPanel>

        <div v-if="imageryError" class="placeholder-banner">{{ imageryError }}</div>

        <div class="analysis-grid">
          <ChartCard
            :title="`指标趋势（${currentMetricName}）`"
            :loading="seriesLoading"
            :empty="!selectedSeriesPoints.length"
            empty-text="选择地块后显示当前指标趋势"
          >
            <template #extra>
              <a-segmented v-model:value="trendDays" :options="trendOptions" size="small" />
            </template>
            <EChartView :option="plotTrendOption" :height="276" />
          </ChartCard>

          <DataTable
            title="关键指标表"
            :columns="metricColumns"
            :data-source="keyMetricRows"
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
        </div>

        <DataTable
          title="最新观测记录"
          :columns="observationColumns"
          :data-source="latestObservationRows"
          :loading="seriesLoading"
          row-key="id"
          empty-text="选择地块后查看最新观测记录"
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
            <template v-if="column.key === 'data_source_id'">
              {{ sourceLabel(record.data_source_id as string | null | undefined) }}
            </template>
            <template v-if="column.key === 'action'">
              <a-button size="small" @click="focusObservation(record.observed_at as string)">查看趋势</a-button>
            </template>
          </template>
        </DataTable>
      </div>

      <aside class="map-workbench__side">
        <section class="panel map-detail">
          <div class="map-detail__title">
            <h2>地块详情</h2>
            <StatusTag :status="selectedStatus" />
          </div>

          <EmptyState v-if="!selectedPlotId" compact description="点击地图地块查看详情" />
          <template v-else>
            <div class="map-detail__hero">
              <strong>{{ selectedProperties?.plot_code || selectedPlotId }}</strong>
              <span>{{ selectedProperties?.region || summary?.plot.region || '--' }}</span>
            </div>

            <dl class="map-detail__list">
              <div>
                <dt>地块名称</dt>
                <dd>{{ summary?.plot.plot_name || selectedProperties?.plot_name || '--' }}</dd>
              </div>
              <div>
                <dt>地块面积</dt>
                <dd>{{ selectedPlotArea }}</dd>
              </div>
              <div>
                <dt>水稻品种</dt>
                <dd>演示品种</dd>
              </div>
              <div>
                <dt>最近观测</dt>
                <dd>{{ activeObservation?.observed_at || selectedProperties?.observed_at || filters.observedAt || '--' }}</dd>
              </div>
              <div>
                <dt>数据来源</dt>
                <dd>{{ sourceLabel(activeObservation?.data_source_id || selectedProperties?.data_source_id) }}</dd>
              </div>
              <div>
                <dt>观测批次</dt>
                <dd>{{ activeObservation?.batch_id || selectedProperties?.batch_id || '--' }}</dd>
              </div>
            </dl>

            <div class="current-metric">
              <span>当前指标（{{ currentMetricName }}）</span>
              <div>
                <strong>{{ selectedProperties?.value ?? activeObservation?.value ?? '--' }}</strong>
                <small>{{ selectedProperties?.unit || activeObservation?.unit || currentMetric?.unit || '' }}</small>
                <StatusTag :status="selectedStatus" />
              </div>
              <p :class="['metric-delta', currentMetricDelta.trend]">
                较昨日 {{ currentMetricDelta.text }}
              </p>
            </div>

            <div class="snapshot-list">
              <h3>关键指标快照</h3>
              <div v-for="item in snapshotRows" :key="item.metric_code">
                <span>{{ item.shortName }}</span>
                <strong>{{ item.value ?? '--' }} <small>{{ item.unit }}</small></strong>
                <StatusTag :status="item.quality_flag" />
              </div>
            </div>

            <div class="map-detail__actions">
              <RouterLink :to="`/plot-detail/${encodeURIComponent(selectedPlotId)}`">
                <a-button type="primary">查看画像</a-button>
              </RouterLink>
              <RouterLink to="/warnings">
                <a-button>关注预警</a-button>
              </RouterLink>
            </div>
          </template>
        </section>

        <section class="panel layer-control">
          <h2>图层控制</h2>
          <div>
            <span>地块边界</span>
            <a-switch v-model:checked="layerToggles.boundaries" size="small" />
          </div>
          <div>
            <span>当前指标渲染</span>
            <a-switch v-model:checked="layerToggles.metric" size="small" />
          </div>
          <div>
            <span>预警地块</span>
            <a-switch v-model:checked="layerToggles.warnings" size="small" />
          </div>
          <div>
            <span>区域边界</span>
            <a-switch v-model:checked="layerToggles.region" size="small" />
          </div>
        </section>
      </aside>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import type { TableColumnsType } from 'ant-design-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

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
import { firstRouteQueryValue } from '@/services/pageLinkage';
import type {
  MapFeature,
  MapFeatureCollection,
  MapFeatureProperties,
  Metric,
  MetricSeries,
  PlotMetricSnapshot,
  PlotSeriesPoint,
  PlotSeriesResponse,
  PlotSummaryResponse,
  RegionCode,
} from '@/types/api';

const emptyCollection: MapFeatureCollection = { type: 'FeatureCollection', features: [] };
const keyMetricCodes = ['crop_growth', 'nitrogen', 'ph', 'leaf_area_index', 'plant_height'];
const shortMetricName: Record<string, string> = {
  crop_growth: '作物长势',
  nitrogen: '氮',
  ph: 'pH',
  leaf_area_index: 'LAI',
  plant_height: '株高',
};

const route = useRoute();
const loading = ref(false);
const seriesLoading = ref(false);
const error = ref('');
const imageryError = ref('');
const metrics = ref<Metric[]>([]);
const dates = ref<string[]>([]);
const featureCollection = ref<MapFeatureCollection>(emptyCollection);
const selectedPlotId = ref(firstRouteQueryValue(route.query.plotId));
const selectedProperties = ref<MapFeatureProperties>();
const summary = ref<PlotSummaryResponse>();
const series = ref<PlotSeriesResponse>();
const trendDays = ref(30);
const trendOptions = [
  { label: '近7天', value: 7 },
  { label: '近15天', value: 15 },
  { label: '近30天', value: 30 },
];

const filters = reactive<{
  region: RegionCode;
  metricCode?: string;
  observedAt?: string;
}>({
  region: 'all',
  metricCode: undefined,
  observedAt: undefined,
});

const layerToggles = reactive({
  boundaries: true,
  metric: true,
  warnings: true,
  region: false,
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

const filteredFeatureCollection = computed<MapFeatureCollection>(() => featureCollection.value);
const selectedFeature = computed<MapFeature | undefined>(() =>
  featureCollection.value.features.find((feature) => feature.properties.plot_id === selectedPlotId.value),
);
const selectedStatus = computed(() => selectedProperties.value?.quality_flag || selectedProperties.value?.status || 'empty');
const selectedPlotArea = computed(() => {
  const area = selectedFeature.value ? calculatePolygonAreaMu(selectedFeature.value) : undefined;
  return area ? `约 ${area.toFixed(1)} 亩` : '--';
});

const activeObservation = computed(() =>
  summary.value?.latest_observations.find((item) => item.metric_code === filters.metricCode),
);
const activeSeries = computed<MetricSeries | undefined>(() =>
  series.value?.series.find((item) => item.metric_code === filters.metricCode) ?? series.value?.series[0],
);
const selectedSeriesPoints = computed(() =>
  [...(activeSeries.value?.points ?? [])]
    .sort((a, b) => a.observed_at.localeCompare(b.observed_at))
    .slice(-trendDays.value),
);
const currentMetricDelta = computed(() => metricDelta(filters.metricCode));

const plotTrendOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 24, right: 18, bottom: 30, left: 44 },
  xAxis: {
    type: 'category',
    data: selectedSeriesPoints.value.map((point) => point.observed_at.slice(5)),
    boundaryGap: false,
    axisLine: { show: false },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#edf2f0' } },
  },
  series: [{
    name: activeSeries.value?.metric_name ?? currentMetricName.value,
    type: 'line',
    smooth: true,
    symbolSize: 6,
    data: selectedSeriesPoints.value.map((point) => point.value),
    lineStyle: { width: 2.5, color: '#15905d' },
    itemStyle: { color: '#15905d' },
    areaStyle: { color: 'rgba(21, 144, 93, 0.10)' },
  }],
}));

const keyMetricRows = computed(() =>
  keyMetricCodes.map((metricCode) => {
    const item = summary.value?.latest_observations.find((record) => record.metric_code === metricCode);
    const delta = metricDelta(metricCode);
    return {
      id: metricCode,
      metric_code: metricCode,
      metric_name: shortMetricName[metricCode] ?? item?.metric_name ?? metricCode,
      value: item?.value ?? null,
      unit: item?.unit ?? '',
      quality_flag: item?.quality_flag ?? 'empty',
      deltaText: delta.text,
    };
  }),
);

const snapshotRows = computed(() =>
  keyMetricRows.value.map((item) => ({
    ...item,
    shortName: shortMetricName[item.metric_code] ?? item.metric_name,
  })),
);

const latestObservationRows = computed(() =>
  [...(activeSeries.value?.points ?? [])]
    .sort((a, b) => b.observed_at.localeCompare(a.observed_at))
    .slice(0, 5)
    .map((item) => ({
      ...item,
      id: `${activeSeries.value?.metric_code}-${item.observed_at}`,
      metric_name: activeSeries.value?.metric_name ?? currentMetricName.value,
      unit: activeSeries.value?.unit ?? currentMetric.value?.unit ?? '',
    })),
);

const metricColumns: TableColumnsType = [
  { title: '指标', dataIndex: 'metric_name', key: 'metric_name' },
  { title: '数值', dataIndex: 'value', key: 'value' },
  { title: '单位', dataIndex: 'unit', key: 'unit', width: 82 },
  { title: '状态', dataIndex: 'quality_flag', key: 'quality_flag', width: 92 },
  { title: '较昨日变化', dataIndex: 'deltaText', key: 'deltaText', width: 116 },
];

const observationColumns: TableColumnsType = [
  { title: '日期', dataIndex: 'observed_at', key: 'observed_at' },
  { title: '指标', dataIndex: 'metric_name', key: 'metric_name' },
  { title: '数值', dataIndex: 'value', key: 'value' },
  { title: '单位', dataIndex: 'unit', key: 'unit', width: 88 },
  { title: '状态', dataIndex: 'quality_flag', key: 'quality_flag', width: 96 },
  { title: '数据来源', dataIndex: 'data_source_id', key: 'data_source_id' },
  { title: '观测批次', dataIndex: 'batch_id', key: 'batch_id' },
  { title: '操作', dataIndex: 'action', key: 'action', width: 108 },
];

onMounted(() => {
  void initialize();
});

watch(
  () => route.query.plotId,
  (plotId) => {
    const nextPlotId = firstRouteQueryValue(plotId);
    if (nextPlotId && nextPlotId !== selectedPlotId.value) {
      selectedPlotId.value = nextPlotId;
      const next = featureCollection.value.features.find((feature) => feature.properties.plot_id === nextPlotId);
      selectedProperties.value = next?.properties;
      void loadSelectedPlot();
    }
  },
);

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
    filters.metricCode = metricData.items.find((item) => item.metric_code === 'chlorophyll')?.metric_code
      ?? metricData.items[0]?.metric_code;
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
      if (next) {
        await loadSelectedPlot();
      }
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
      fetchPlotSeries({ plotId: selectedPlotId.value }),
    ]);
    summary.value = summaryData;
    series.value = seriesData;
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '地块详情或趋势加载失败。');
  } finally {
    seriesLoading.value = false;
  }
}

function resetFilters() {
  filters.region = 'all';
  filters.metricCode = metrics.value.find((item) => item.metric_code === 'chlorophyll')?.metric_code
    ?? metrics.value[0]?.metric_code;
  filters.observedAt = dates.value[dates.value.length - 1];
}

function focusObservation(observedAt: string) {
  filters.observedAt = observedAt;
}

function sourceLabel(value?: string | null) {
  if (!value) {
    return '--';
  }
  if (value.includes('simulated') || value.includes('demo')) {
    return '模拟数据';
  }
  if (value.includes('generated')) {
    return '程序生成';
  }
  return value;
}

function metricDelta(metricCode?: string) {
  const targetSeries = series.value?.series.find((item) => item.metric_code === metricCode);
  const points = [...(targetSeries?.points ?? [])].sort((a, b) => a.observed_at.localeCompare(b.observed_at));
  if (points.length < 2) {
    return { text: '--', trend: 'flat' };
  }

  const selectedIndex = filters.observedAt
    ? points.findIndex((point) => point.observed_at === filters.observedAt)
    : points.length - 1;
  const index = selectedIndex > 0 ? selectedIndex : points.length - 1;
  const current = points[index];
  const previous = points[index - 1];
  const currentValue = Number(current?.value);
  const previousValue = Number(previous?.value);
  if (!Number.isFinite(currentValue) || !Number.isFinite(previousValue)) {
    return { text: '--', trend: 'flat' };
  }

  const change = Math.round((currentValue - previousValue) * 100) / 100;
  const unit = targetSeries?.unit ? ` ${targetSeries.unit}` : '';
  if (change > 0) {
    return { text: `↑ ${change}${unit}`, trend: 'up' };
  }
  if (change < 0) {
    return { text: `↓ ${Math.abs(change)}${unit}`, trend: 'down' };
  }
  return { text: `持平${unit}`, trend: 'flat' };
}

function calculatePolygonAreaMu(feature: MapFeature) {
  if (feature.geometry.type !== 'Polygon' || !Array.isArray(feature.geometry.coordinates)) {
    return undefined;
  }
  const ring = feature.geometry.coordinates[0];
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
  for (let i = 0; i < projected.length; i += 1) {
    const [x1, y1] = projected[i];
    const [x2, y2] = projected[(i + 1) % projected.length];
    area += x1 * y2 - x2 * y1;
  }
  return Math.abs(area) / 2 / 666.667;
}

</script>

<style scoped>
.map-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: start;
}

.map-workbench__main,
.map-workbench__side {
  display: grid;
  min-width: 0;
  gap: 16px;
}

.map-filter-bar {
  width: 100%;
  max-width: none;
  border-color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 28px rgba(7, 36, 26, 0.20);
  gap: 10px;
  padding: 12px 14px;
  backdrop-filter: blur(8px);
}

.map-filter-bar :deep(.filter-bar__content) {
  gap: 10px;
}

.map-filter-bar :deep(.ant-select),
.map-filter-bar :deep(.ant-picker) {
  min-width: 164px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(380px, 0.65fr);
  gap: 16px;
}

.map-detail,
.layer-control {
  padding: 20px;
}

.map-detail__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.map-detail__title h2,
.layer-control h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
}

.map-detail__hero {
  border-bottom: 1px solid var(--rf-border-soft);
  margin-top: 16px;
  padding-bottom: 16px;
}

.map-detail__hero strong {
  display: block;
  color: var(--rf-text);
  font-size: 32px;
  font-weight: 900;
  line-height: 1.1;
}

.map-detail__hero span {
  display: block;
  margin-top: 6px;
  color: var(--rf-text-muted);
  font-size: 13px;
}

.map-detail__list {
  display: grid;
  gap: 10px;
  margin: 16px 0;
}

.map-detail__list div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.map-detail__list dt {
  color: var(--rf-text-muted);
  font-size: 13px;
}

.map-detail__list dd {
  margin: 0;
  text-align: right;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 750;
}

.current-metric {
  border-top: 1px solid var(--rf-border-soft);
  border-bottom: 1px solid var(--rf-border-soft);
  padding: 16px 0;
}

.current-metric > span {
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 800;
}

.current-metric div {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 8px;
}

.current-metric strong {
  color: var(--rf-text);
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
}

.current-metric small {
  color: var(--rf-text-muted);
  font-size: 14px;
  font-weight: 700;
}

.metric-delta {
  margin: 8px 0 0;
  font-size: 13px;
  font-weight: 800;
}

.metric-delta.up {
  color: var(--rf-status-normal);
}

.metric-delta.down {
  color: var(--rf-status-critical);
}

.metric-delta.flat {
  color: var(--rf-text-muted);
}

.snapshot-list {
  display: grid;
  gap: 11px;
  margin-top: 16px;
}

.snapshot-list h3 {
  margin: 0 0 2px;
  font-size: 14px;
  font-weight: 800;
}

.snapshot-list div {
  display: grid;
  grid-template-columns: minmax(72px, 1fr) auto auto;
  gap: 10px;
  align-items: center;
}

.snapshot-list span {
  color: var(--rf-text);
  font-size: 13px;
}

.snapshot-list strong {
  font-size: 13px;
  font-weight: 800;
  text-align: right;
}

.snapshot-list small {
  color: var(--rf-text-muted);
  font-weight: 600;
}

.map-detail__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 20px;
}

.map-detail__actions a,
.map-detail__actions :deep(.ant-btn) {
  width: 100%;
}

.layer-control {
  display: grid;
  gap: 14px;
}

.layer-control div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--rf-text);
  font-size: 13px;
}

.map-legend {
  display: grid;
  gap: 8px;
  min-width: 210px;
}

.map-legend strong,
.map-legend span,
.map-legend__scale {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 12px;
}

.map-legend strong {
  font-size: 13px;
}

.map-legend__scale i {
  flex: 1;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, #13784f, #d8d537 52%, #ea580c);
}

.map-legend b {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

.legend-empty {
  background: #d1d5db;
}

.legend-boundary {
  border: 2px solid #fff;
  background: transparent;
}

.legend-warning {
  background: var(--rf-status-warning);
}

@media (max-width: 1280px) {
  .map-workbench,
  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .map-filter-bar {
    width: 100%;
  }
}

@media (max-width: 720px) {
  .map-filter-bar {
    width: 100%;
  }

  .map-detail__actions {
    grid-template-columns: 1fr;
  }
}
</style>
