<template>
  <div class="flex min-h-[calc(100vh-2rem)] flex-col gap-4">
    <CommandBar title="Cesium 地图孪生" description="程序生成地块边界、指标着色、地块点击和趋势联动。">
      <template #actions>
        <div class="flex flex-wrap items-center gap-2">
          <Select v-model="filters.metricCode" :disabled="loading">
            <SelectTrigger class="w-44">
              <SelectValue placeholder="选择指标" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="metric in metricOptions" :key="metric.value" :value="metric.value">
                  {{ metric.label }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Select v-model="filters.observedAt" :disabled="loading">
            <SelectTrigger class="w-40">
              <SelectValue placeholder="选择日期" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="date in dates" :key="date" :value="date">
                  {{ date }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Select v-model="filters.region" :disabled="loading">
            <SelectTrigger class="w-32">
              <SelectValue placeholder="区域" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="all">全部区域</SelectItem>
                <SelectItem value="east">试验一区</SelectItem>
                <SelectItem value="west">试验二区</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <input
            v-model="plotKeyword"
            class="h-9 w-40 rounded-md border border-input bg-background px-3 text-sm outline-none focus:ring-1 focus:ring-ring"
            placeholder="搜索地块编号"
          >
          <Button :disabled="loading" @click="loadMap">
            {{ loading ? '刷新中' : '刷新图层' }}
          </Button>
        </div>
      </template>
    </CommandBar>

    <ErrorState v-if="error" :message="error" compact />

    <section class="grid min-h-0 flex-1 grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
      <TwinMapPanel>
        <CesiumMapPanel
          title=""
          :feature-collection="filteredFeatureCollection"
          :loading="loading"
          :selected-plot-id="selectedPlotId"
          :height="620"
          @plot-click="handlePlotClick"
          @imagery-error="imageryError = $event"
        >
          <template #toolbar>
            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="selectFirstPlot">定位首个地块</Button>
              <Button variant="outline" size="sm" @click="clearSelection">清除选择</Button>
            </div>
          </template>
          <template #legend>
            <div class="map-legend">
              <strong>{{ currentMetricName }}</strong>
              <span><i class="legend-good" />有效数据</span>
              <span><i class="legend-warning" />临界/缺失</span>
              <span><i class="legend-error" />异常/错误</span>
              <span><i class="legend-empty" />无数据</span>
            </div>
          </template>
        </CesiumMapPanel>
      </TwinMapPanel>

      <InspectorPanel
        title="地块详情"
        :description="selectedPlotId ? '已选择地块' : '点击地图地块查看详情'"
      >
        <template #actions>
          <StatusBadge :status="selectedProperties?.quality_flag || selectedProperties?.status || 'no_data'" />
        </template>

        <div v-if="!selectedPlotId" class="grid min-h-32 place-items-center rounded-md border border-dashed border-border text-sm text-muted-foreground">
          尚未选择地块
        </div>
        <template v-else>
          <div class="flex items-center justify-between gap-3 border-b border-border pb-4">
            <strong class="text-2xl font-semibold">{{ selectedProperties?.plot_code || selectedPlotId }}</strong>
            <span class="text-sm text-muted-foreground">{{ selectedProperties?.region || summary?.plot.region || '--' }}</span>
          </div>
          <dl class="mt-4 grid gap-3">
            <div class="flex items-center justify-between gap-3 rounded-md border border-border bg-muted/35 px-3 py-2">
              <dt class="text-sm text-muted-foreground">当前指标</dt>
              <dd class="m-0 text-right text-sm font-medium">{{ currentMetricName }}</dd>
            </div>
            <div class="flex items-center justify-between gap-3 rounded-md border border-border bg-muted/35 px-3 py-2">
              <dt class="text-sm text-muted-foreground">当前值</dt>
              <dd class="m-0 text-right">
                <MetricValue label="指标值" :value="selectedProperties?.value" :unit="selectedProperties?.unit" />
              </dd>
            </div>
            <div class="flex items-center justify-between gap-3 rounded-md border border-border bg-muted/35 px-3 py-2">
              <dt class="text-sm text-muted-foreground">观测日期</dt>
              <dd class="m-0 text-right text-sm font-medium">{{ selectedProperties?.observed_at || filters.observedAt || '--' }}</dd>
            </div>
            <div class="flex items-center justify-between gap-3 rounded-md border border-border bg-muted/35 px-3 py-2">
              <dt class="text-sm text-muted-foreground">观测批次</dt>
              <dd class="m-0 text-right text-sm font-medium">{{ activeObservation?.batch_id || selectedProperties?.batch_id || '--' }}</dd>
            </div>
            <div class="flex items-center justify-between gap-3 rounded-md border border-border bg-muted/35 px-3 py-2">
              <dt class="text-sm text-muted-foreground">数据来源</dt>
              <dd class="m-0 text-right text-sm font-medium">{{ activeObservation?.data_source_id || selectedProperties?.data_source_id || '--' }}</dd>
            </div>
          </dl>
          <Button class="mt-4 w-full" @click="router.push(plotDetailRoute)">查看地块画像</Button>
        </template>
      </InspectorPanel>
    </section>

    <div v-if="imageryError" class="placeholder-banner">{{ imageryError }}</div>

    <section class="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(320px,0.6fr)]">
      <ChartCard title="当前地块趋势" :loading="seriesLoading" :empty="!selectedSeriesPoints.length" empty-text="选择地块后显示趋势">
        <EChartView :option="plotTrendOption" :height="280" />
      </ChartCard>

      <DataPanel title="当前筛选摘要">
        <div class="grid grid-cols-2 gap-3">
          <MetricValue label="地块数量" :value="filteredFeatureCollection.features.length" />
          <MetricValue label="有效数据占比" :value="validRate" unit="%" />
          <MetricValue label="区域" :value="regionLabel" />
          <MetricValue label="日期" :value="filters.observedAt || '最新'" />
        </div>
      </DataPanel>
    </section>

    <DataPanel title="关键指标表" description="当前地块的指标快照、批次、来源和质量状态。">
      <div v-if="seriesLoading" class="py-8 text-center text-sm text-muted-foreground">正在加载关键指标...</div>
      <div v-else-if="!summaryRows.length" class="py-8 text-center text-sm text-muted-foreground">选择地块后查看关键指标</div>
      <Table v-else>
        <TableHeader>
          <TableRow>
            <TableHead>指标</TableHead>
            <TableHead>当前值</TableHead>
            <TableHead>观测日期</TableHead>
            <TableHead>质量状态</TableHead>
            <TableHead>观测批次</TableHead>
            <TableHead>数据来源</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="row in summaryRows" :key="row.id">
            <TableCell>{{ row.metric_name }}</TableCell>
            <TableCell>{{ formatMetricCell(row.value, row.unit) }}</TableCell>
            <TableCell>{{ row.observed_at }}</TableCell>
            <TableCell><StatusBadge :status="row.quality_flag" /></TableCell>
            <TableCell>{{ row.batch_id }}</TableCell>
            <TableCell>{{ row.data_source_id }}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </DataPanel>
  </div>
</template>

<script setup lang="ts">
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import {
  fetchDates,
  fetchMapLayers,
  fetchMetrics,
  fetchPlotSeries,
  fetchPlotSummary,
  getApiErrorMessage,
} from '@/api';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  CesiumMapPanel,
  ChartCard,
  EChartView,
  ErrorState,
} from '@/components/base';
import {
  CommandBar,
  DataPanel,
  InspectorPanel,
  MetricValue,
  StatusBadge,
  TwinMapPanel,
} from '@/components/workbench';
import { findFeatureByPlotId } from '@/services/mapAnalysis';
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

const route = useRoute();
const router = useRouter();
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
let suppressFilterReload = false;
let mapRequestId = 0;
let selectedPlotRequestId = 0;

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
const routePlotId = computed(() => {
  const value = route.query.plotId;
  const plotId = Array.isArray(value) ? value[0] : value;
  return typeof plotId === 'string' && plotId.trim() ? plotId : undefined;
});
const plotDetailRoute = computed(() => ({
  name: 'plot-detail',
  params: { plotId: selectedPlotId.value },
}));

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
    lineStyle: { width: 3, color: '#07883f' },
    itemStyle: { color: '#07883f' },
    areaStyle: { color: 'rgba(7, 136, 63, 0.10)' },
    markLine: filters.observedAt ? {
      symbol: 'none',
      label: { formatter: '当前日期', color: '#22513a' },
      lineStyle: { color: '#f59e0b', type: 'dashed', width: 2 },
      data: [{ xAxis: filters.observedAt }],
    } : undefined,
  }],
}));

const summaryRows = computed(() =>
  (summary.value?.latest_observations ?? []).map((item) => ({
    ...item,
    id: `${item.metric_code}-${item.observed_at}`,
  })),
);

onMounted(() => {
  void initialize();
});

watch(
  () => [filters.region, filters.metricCode, filters.observedAt],
  () => {
    if (suppressFilterReload) {
      return;
    }
    void loadMap();
  },
);

watch(
  routePlotId,
  () => {
    selectRoutePlotFromCurrentLayer();
  },
);

async function initialize() {
  loading.value = true;
  suppressFilterReload = true;
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
    suppressFilterReload = false;
    loading.value = false;
  }
}

async function loadMap() {
  if (!filters.metricCode) {
    return;
  }
  const requestId = ++mapRequestId;
  loading.value = true;
  error.value = '';
  try {
    const response = await fetchMapLayers({
      region: filters.region,
      metricCode: filters.metricCode,
      observedAt: filters.observedAt,
    });
    if (requestId !== mapRequestId) {
      return;
    }

    featureCollection.value = response.layers[0]?.feature_collection ?? emptyCollection;
    if (selectRoutePlotFromCurrentLayer()) {
      return;
    }
    if (selectedPlotId.value) {
      const next = findFeatureByPlotId(featureCollection.value, selectedPlotId.value);
      selectedProperties.value = next?.properties;
      if (next) {
        await loadSelectedPlot();
      } else {
        selectedPlotRequestId += 1;
        summary.value = undefined;
        series.value = undefined;
      }
    }
  } catch (currentError) {
    if (requestId === mapRequestId) {
      error.value = getApiErrorMessage(currentError, '地图图层加载失败，请检查 /api/map/layers。');
    }
  } finally {
    if (requestId === mapRequestId) {
      loading.value = false;
    }
  }
}

async function handlePlotClick(properties: MapFeatureProperties) {
  if (!properties.plot_id) {
    return;
  }
  selectedPlotId.value = properties.plot_id;
  selectedProperties.value = properties;
  await syncPlotQuery(properties.plot_id);
  await loadSelectedPlot();
}

async function loadSelectedPlot() {
  if (!selectedPlotId.value) {
    return;
  }
  const requestId = ++selectedPlotRequestId;
  seriesLoading.value = true;
  try {
    const [summaryData, seriesData] = await Promise.all([
      fetchPlotSummary(selectedPlotId.value),
      fetchPlotSeries({ plotId: selectedPlotId.value, metricCode: filters.metricCode }),
    ]);
    if (requestId === selectedPlotRequestId) {
      summary.value = summaryData;
      series.value = seriesData;
    }
  } catch (currentError) {
    if (requestId === selectedPlotRequestId) {
      error.value = getApiErrorMessage(currentError, '地块详情或趋势加载失败。');
    }
  } finally {
    if (requestId === selectedPlotRequestId) {
      seriesLoading.value = false;
    }
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
  selectedPlotRequestId += 1;
  void syncPlotQuery(undefined);
}

function selectRoutePlotFromCurrentLayer() {
  if (!routePlotId.value) {
    return false;
  }

  const feature = findFeatureByPlotId(featureCollection.value, routePlotId.value);
  if (!feature) {
    return false;
  }

  if (selectedPlotId.value === routePlotId.value && selectedProperties.value?.plot_id === routePlotId.value) {
    return true;
  }

  selectedPlotId.value = routePlotId.value;
  selectedProperties.value = feature.properties;
  void loadSelectedPlot();
  return true;
}

async function syncPlotQuery(plotId: string | undefined) {
  const currentPlotId = routePlotId.value;
  if (plotId === currentPlotId || (!plotId && !currentPlotId)) {
    return;
  }

  const nextQuery = { ...route.query };
  if (plotId) {
    nextQuery.plotId = plotId;
  } else {
    delete nextQuery.plotId;
  }
  await router.replace({ name: 'map-twin', query: nextQuery });
}

function formatMetricCell(value: number | string | null | undefined, unit?: string | null) {
  if (value === null || value === undefined || value === '') {
    return '--';
  }
  return `${value}${unit ? ` ${unit}` : ''}`;
}
</script>

<style scoped>
.map-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: stretch;
}

.map-workbench :deep(.page-container__heading) {
  align-items: center;
}

.map-workbench :deep(.filter-bar) {
  position: sticky;
  top: 12px;
  z-index: 9;
}

.map-workbench :deep(.map-panel) {
  min-height: 100%;
}

.map-detail {
  display: flex;
  flex-direction: column;
  align-self: stretch;
  min-height: 100%;
  padding: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.96)),
    var(--rf-surface);
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
  font-size: 30px;
  font-weight: 900;
  letter-spacing: 0;
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
  border: 1px solid var(--rf-border-soft);
  border-radius: var(--rf-radius-lg);
  background: var(--rf-bg-soft);
  padding: 10px 12px;
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
  border: 1px solid var(--rf-border-overlay);
  border-radius: var(--rf-radius-xl);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: var(--rf-shadow-overlay);
  padding: 12px;
  backdrop-filter: blur(14px);
}

.map-legend strong,
.map-legend span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--rf-text);
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
  background: #f59e0b;
}

.legend-error {
  background: #ef4444;
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
  border-radius: var(--rf-radius-lg);
  background: var(--rf-bg-soft);
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

  .map-workbench :deep(.filter-bar) {
    position: static;
  }
}
</style>
