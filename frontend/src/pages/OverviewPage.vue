<template>
  <main class="overview-workbench">
    <CommandBar title="场景驾驶舱" description="稻田数字孪生场景、地块、指标和质量状态总览">
      <template #actions>
        <RouterLink :to="mapRoute" class="overview-command-link">打开地图页</RouterLink>
      </template>
    </CommandBar>

    <ErrorState v-if="error" :message="error" compact />

    <section class="mission-control">
      <aside class="workbench-rail">
        <section class="workbench-panel plot-panel">
          <div class="panel-heading">
            <div>
              <h2>地块列表</h2>
              <p>{{ filteredFeatureCollection.features.length }} 个地块 · 当前 {{ currentMetricName }}</p>
            </div>
            <button type="button" class="panel-action" @click="selectFirstPlot">定位</button>
          </div>
          <div class="plot-search">
            <input v-model="plotKeyword" placeholder="搜索地块编号 / 名称">
            <button type="button" aria-label="筛选地块">筛选</button>
          </div>
          <div class="plot-list">
            <button
              v-for="feature in plotList"
              :key="feature.properties.plot_id"
              type="button"
              class="plot-list__item"
              :class="{ 'is-active': feature.properties.plot_id === selectedPlotId }"
              @click="handlePlotClick(feature.properties)"
            >
              <span>
                <i />
                <strong>{{ feature.properties.plot_code || feature.properties.plot_id }}</strong>
                <small>{{ getPlotName(feature.properties) }} · {{ getCropType(feature.properties) }}</small>
              </span>
              <b>
                <small>{{ getPlotArea(feature.properties) }}</small>
                {{ getHealthScore(feature.properties) }}
              </b>
            </button>
          </div>
          <footer class="panel-foot">
            <span>共 {{ featureCollection.features.length }} 个地块</span>
            <span>1 / 1</span>
          </footer>
        </section>

        <section class="workbench-panel control-panel">
          <div class="panel-heading">
            <div>
              <h2>图层控制</h2>
              <p>空间图层与透明度</p>
            </div>
          </div>
          <div class="layer-list">
            <label><input type="checkbox" checked disabled /> 地块边界 <span>ON</span></label>
            <label><input type="checkbox" checked disabled /> NDVI 合成 <span>ON</span></label>
            <label><input type="checkbox" disabled /> 土壤湿度 <span>待接入</span></label>
            <label><input type="checkbox" checked disabled /> 预警点位 <span>{{ warnings.length }}</span></label>
            <label><input type="checkbox" checked disabled /> 传感器站点 <span>模拟</span></label>
          </div>
          <div class="opacity-control">
            <span>透明度</span>
            <input type="range" min="0" max="100" value="70" disabled>
            <b>70%</b>
          </div>
        </section>

        <section class="workbench-panel scenario-panel">
          <div class="panel-heading">
            <div>
              <h2>场景切换</h2>
              <p>当前模拟数据状态</p>
            </div>
          </div>
          <div class="scenario-tabs">
            <button type="button" class="is-active">早稻生长监测</button>
            <button type="button" disabled>长势对比分析</button>
            <button type="button" disabled>病虫害监测</button>
          </div>
          <div class="source-list">
            <span><i /> 遥感影像源 <b>正常</b></span>
            <span><i /> 气象模拟 <b>正常</b></span>
            <span><i /> 土壤栅格 <b>待接入</b></span>
            <span><i /> 农事记录 <b>更新中</b></span>
          </div>
        </section>

        <section class="workbench-panel phase-panel">
          <div class="panel-heading">
            <div>
              <h2>生育期时间轴</h2>
              <p>{{ activeGrowthStage.name }} · 观测 {{ selectedDate || '--' }}</p>
            </div>
          </div>
          <ol class="compact-timeline">
            <li
              v-for="stage in growthStages"
              :key="stage.name"
              :class="{ 'is-active': stage.active }"
            >
              <span>{{ stage.name }}</span>
            </li>
          </ol>
          <div class="phase-meta">
            <span>播种期 2025-06-01</span>
            <span>预计收穗 2025-07-15</span>
          </div>
        </section>
      </aside>

      <section class="map-workspace">
        <CesiumMapPanel
          title=""
          :feature-collection="filteredFeatureCollection"
          :loading="loading"
          :selected-plot-id="selectedPlotId"
          :height="mapHeight"
          @plot-click="handlePlotClick"
          @imagery-error="imageryError = $event"
        >
          <template #legend>
            <div class="map-legend-card">
              <strong>图例</strong>
              <span><i class="legend-good" />健康地块</span>
              <span><i class="legend-warning" />预警点位</span>
              <span><i class="legend-teal" />传感器站点</span>
            </div>
          </template>
        </CesiumMapPanel>
        <div class="map-statusbar">
          <span><i class="dot-good" />地块边界</span>
          <span><i class="dot-warning" />预警点位 {{ warnings.length }}</span>
          <span><i class="dot-teal" />传感器站点</span>
          <button type="button" @click="loadMap()">刷新图层</button>
          <RouterLink :to="mapRoute">打开地图页</RouterLink>
        </div>
        <div class="map-points" aria-hidden="true">
          <i class="map-point map-point--sensor map-point--a" />
          <i class="map-point map-point--warning map-point--b" />
          <i class="map-point map-point--sensor map-point--c" />
        </div>
        <div class="map-compass" aria-hidden="true">
          <b>N</b>
          <span />
        </div>
        <div v-if="imageryError" class="placeholder-banner">{{ imageryError }}</div>
      </section>

      <aside class="plot-inspector">
        <section class="workbench-panel plot-profile-card">
          <div class="inspector-head">
            <div>
              <span>当前地块</span>
              <h2>{{ selectedPlotCode }} {{ selectedPlotName }}</h2>
            </div>
            <div class="inspector-actions">
              <button type="button" aria-label="收藏地块">☆</button>
              <button type="button" aria-label="更多操作">⋮</button>
            </div>
          </div>

          <div class="plot-tags">
            <StatusBadge :status="selectedProperties?.quality_flag || selectedProperties?.status || 'normal'" />
            <span>{{ selectedCropType }}</span>
            <span>{{ selectedPlotArea }}</span>
            <span>{{ selectedProperties?.region || summary?.plot.region || '--' }}</span>
          </div>

          <div class="inspector-tabs" role="tablist" aria-label="地块详情">
            <button
              v-for="tab in inspectorTabs"
              :key="tab.value"
              type="button"
              :class="{ 'is-active': activeInspectorTab === tab.value }"
              @click="activeInspectorTab = tab.value"
            >
              {{ tab.label }}
            </button>
          </div>

          <template v-if="activeInspectorTab === 'profile'">
            <div class="stage-card">
              <div class="stage-card__copy">
                <span>作物阶段</span>
                <strong>{{ activeGrowthStage.name }}</strong>
                <small>观测日期 {{ selectedProperties?.observed_at || selectedDate || '--' }}</small>
              </div>
              <ol class="stage-track">
                <li
                  v-for="stage in growthStages"
                  :key="stage.name"
                  :class="{ 'is-active': stage.active }"
                >
                  {{ stage.name }}
                </li>
              </ol>
            </div>

            <div class="inspector-grid">
              <div class="inspector-metric inspector-metric--score">
                <span>健康评分</span>
                <strong>{{ healthScore }}</strong>
                <small>/100 · 较昨日 ↑ 3</small>
              </div>
              <div class="inspector-metric">
                <span>NDVI 均值</span>
                <strong>{{ metricSnapshot('ndvi') }}</strong>
                <small>遥感模拟</small>
              </div>
              <div class="inspector-metric">
                <span>土壤湿度</span>
                <strong>{{ metricSnapshot('soil') }}</strong>
                <small>未接入则显示 --</small>
              </div>
              <div class="inspector-metric">
                <span>降水 / 气象</span>
                <strong>{{ metricSnapshot('weather') }}</strong>
                <small>气温 / 降雨相关</small>
              </div>
            </div>

            <div class="risk-panel">
              <div class="panel-heading panel-heading--compact">
                <h3>风险预警</h3>
                <span>{{ selectedWarnings.length }} 条</span>
              </div>
              <ul>
                <li v-if="selectedWarnings.length === 0">当前地块暂无预警</li>
                <li v-for="item in selectedWarnings.slice(0, 3)" :key="item.warning_id">
                  {{ item.metric_name }} · {{ item.message }}
                </li>
              </ul>
            </div>

            <div class="advice-panel">
              <div class="panel-heading panel-heading--compact">
                <h3>决策建议</h3>
              </div>
              <ul>
                <li v-for="item in decisionSuggestions" :key="item">{{ item }}</li>
              </ul>
              <footer>生成时间：{{ selectedDate || '--' }}</footer>
            </div>
          </template>

          <div v-else-if="activeInspectorTab === 'plan'" class="inspector-placeholder">
            <strong>作业计划</strong>
            <span>当前阶段仅展示模拟计划，不输出具体农艺处方。</span>
            <ul>
              <li v-for="event in farmingEvents.slice(0, 3)" :key="event.name">{{ event.date }} · {{ event.name }}</li>
            </ul>
          </div>

          <div v-else class="inspector-placeholder">
            <strong>历史记录</strong>
            <span>观测批次、数据来源和质量标记将在此持续归档。</span>
            <ul>
              <li v-for="batch in observationBatches.slice(0, 3)" :key="batch.id">{{ batch.id }} · {{ batch.date }}</li>
            </ul>
          </div>
        </section>
      </aside>
    </section>

    <section class="analysis-dock">
      <ChartCard title="NDVI 趋势" :loading="seriesLoading" :empty="!selectedSeriesPoints.length" empty-text="选择地块后显示趋势">
        <EChartView :option="ndviOption" :height="178" />
      </ChartCard>

      <ChartCard title="土壤湿度趋势" :loading="seriesLoading" :empty="!soilSeriesPoints.length" empty-text="当前指标字典暂未接入土壤湿度时序">
        <EChartView :option="soilMoistureOption" :height="178" />
      </ChartCard>

      <section class="workbench-panel batch-panel">
        <div class="panel-heading">
          <div>
            <h2>观测批次</h2>
            <p>批次、来源和状态可追溯</p>
          </div>
        </div>
        <ul>
          <li v-for="batch in observationBatches" :key="batch.id">
            <strong>{{ batch.id }}</strong>
            <span>{{ batch.date }} · {{ batch.source }} · {{ batch.count || '模拟' }} 项指标</span>
          </li>
        </ul>
      </section>

      <section class="workbench-panel event-panel">
        <div class="panel-heading">
          <div>
            <h2>农事情景事件</h2>
            <p>仅用于答辩演示叙事</p>
          </div>
        </div>
        <ul>
          <li v-for="event in farmingEvents" :key="event.name">
            <span>{{ event.date }}</span>
            <strong>{{ event.name }}</strong>
          </li>
        </ul>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref } from 'vue';

import {
  fetchDates,
  fetchMapLayers,
  fetchMetrics,
  fetchPlotSeries,
  fetchPlotSummary,
  fetchScenarioOverview,
  fetchWarnings,
  getApiErrorMessage,
} from '@/api';
import {
  CesiumMapPanel,
  ChartCard,
  EChartView,
  ErrorState,
} from '@/components/base';
import {
  CommandBar,
  StatusBadge,
} from '@/components/workbench';
import { formatTwinDateRange, getOverviewApiErrorMessage } from '@/services/overview';
import type {
  MapFeatureCollection,
  MapFeatureProperties,
  Metric,
  PlotSeriesResponse,
  PlotSummaryResponse,
  RegionCode,
  ScenarioOverviewResponse,
  WarningItem,
} from '@/types/api';

const emptyCollection: MapFeatureCollection = { type: 'FeatureCollection', features: [] };

const loading = ref(false);
const seriesLoading = ref(false);
const error = ref('');
const imageryError = ref('');
const overview = ref<ScenarioOverviewResponse>();
const metrics = ref<Metric[]>([]);
const featureCollection = ref<MapFeatureCollection>(emptyCollection);
const selectedPlotId = ref('');
const selectedProperties = ref<MapFeatureProperties>();
const summary = ref<PlotSummaryResponse>();
const series = ref<PlotSeriesResponse>();
const warnings = ref<WarningItem[]>([]);
const plotKeyword = ref('');
const activeInspectorTab = ref<'profile' | 'plan' | 'history'>('profile');
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

const currentMetric = computed(() => metrics.value.find((item) => item.metric_code === filters.metricCode));
const currentMetricName = computed(() => currentMetric.value?.metric_name ?? '默认指标');
const selectedDate = computed(() => filters.observedAt || overview.value?.default_observed_at);
const healthScore = computed(() => `${overview.value?.health_score ?? '--'}`);
const dateRangeLabel = computed(() =>
  overview.value ? formatTwinDateRange(overview.value.scenario.date_range) : '加载中',
);
const selectedPlotCode = computed(() =>
  selectedProperties.value?.plot_code || summary.value?.plot.plot_code || selectedPlotId.value || '尚未选择',
);
const selectedPlotName = computed(() =>
  selectedProperties.value?.plot_name || summary.value?.plot.plot_name || getPlotName(selectedProperties.value),
);
const selectedCropType = computed(() => getCropType(selectedProperties.value));
const selectedPlotArea = computed(() => getPlotArea(selectedProperties.value));
const mapHeight = computed(() => 620);
const mapRoute = computed(() => ({
  name: 'map-twin',
  query: selectedPlotId.value ? { plotId: selectedPlotId.value } : undefined,
}));
const inspectorTabs = [
  { label: '地块画像', value: 'profile' as const },
  { label: '作业计划', value: 'plan' as const },
  { label: '历史记录', value: 'history' as const },
];

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
const plotList = computed(() => filteredFeatureCollection.value.features.slice(0, 8));
const selectedWarnings = computed(() =>
  warnings.value.filter((item) => item.plot_id === selectedPlotId.value),
);
const activeSeries = computed(() =>
  series.value?.series.find((item) => item.metric_code.toLowerCase().includes('ndvi'))
  ?? series.value?.series.find((item) => item.metric_code === filters.metricCode)
  ?? series.value?.series[0],
);
const soilSeries = computed(() =>
  series.value?.series.find((item) =>
    item.metric_code.toLowerCase().includes('soil')
    || item.metric_name.includes('土壤')
    || item.metric_name.includes('含水'),
  ),
);
const selectedSeriesPoints = computed(() =>
  [...(activeSeries.value?.points ?? [])].sort((a, b) => a.observed_at.localeCompare(b.observed_at)),
);
const soilSeriesPoints = computed(() =>
  [...(soilSeries.value?.points ?? [])].sort((a, b) => a.observed_at.localeCompare(b.observed_at)),
);
const observationBatches = computed(() => {
  const observations = summary.value?.latest_observations ?? [];
  const rows = Array.from(
    observations.reduce((map, item) => {
      const current = map.get(item.batch_id);
      map.set(item.batch_id, {
        id: item.batch_id,
        date: item.observed_at,
        source: item.data_source_id,
        count: (current?.count ?? 0) + 1,
      });
      return map;
    }, new Map<string, { id: string; date: string; source: string; count: number }>()),
  ).map(([, value]) => value).slice(0, 5);
  if (rows.length) {
    return rows;
  }
  return (summary.value?.batch_ids ?? []).slice(0, 5).map((id) => ({
    id,
    date: selectedDate.value || '--',
    source: 'simulated-source',
    count: 0,
  }));
});

const growthStages = computed(() => [
  { name: '播种', date: '04-05', active: false, progress: '8%' },
  { name: '移栽', date: '04-18', active: false, progress: '22%' },
  { name: '返青', date: '04-25', active: false, progress: '36%' },
  { name: '分蘖', date: '05-10', active: false, progress: '52%' },
  { name: '拔节', date: '05-24', active: true, progress: '66%' },
  { name: '孕穗', date: '06-10', active: false, progress: '82%' },
  { name: '抽穗', date: '06-30', active: false, progress: '94%' },
]);
const activeGrowthStage = computed(() =>
  growthStages.value.find((stage) => stage.active) ?? growthStages.value[0],
);
const farmingEvents = [
  { date: '04-18', name: '移栽完成' },
  { date: '04-28', name: '第一次追肥' },
  { date: '05-12', name: '病虫害巡田' },
  { date: '06-03', name: '拔节期管理计划' },
];
const decisionSuggestions = computed(() => {
  if (selectedWarnings.value.length) {
    return [
      '优先复核当前地块的异常指标与观测批次。',
      '对照遥感来源与模拟规则，确认是否为缺失或离群记录。',
      '必要时安排现场核验，不在系统内输出农艺处方。',
    ];
  }
  return [
    '维持当前观测节奏，关注下一批次遥感指标变化。',
    '保留批次来源和质量标记，便于答辩追溯。',
    '后续接入合规土壤湿度和气象数据后再扩展建议。',
  ];
});

const ndviOption = computed<EChartsOption>(() => buildLineOption(
  selectedSeriesPoints.value.map((point) => point.observed_at),
  selectedSeriesPoints.value.map((point) => Number(point.value ?? 0)),
  activeSeries.value?.metric_name ?? 'NDVI',
  '#087443',
));
const soilMoistureOption = computed<EChartsOption>(() => buildLineOption(
  soilSeriesPoints.value.map((point) => point.observed_at),
  soilSeriesPoints.value.map((point) => Number(point.value ?? 0)),
  soilSeries.value?.metric_name ?? '土壤湿度',
  '#0c9488',
));

onMounted(() => {
  void initialize();
});

async function initialize() {
  loading.value = true;
  try {
    const [overviewData, metricData, dateData, warningData] = await Promise.all([
      fetchScenarioOverview(),
      fetchMetrics(),
      fetchDates(),
      fetchWarnings(),
    ]);
    overview.value = overviewData;
    metrics.value = metricData.items;
    warnings.value = warningData.items;
    filters.metricCode = overviewData.default_metric_code || metricData.items[0]?.metric_code;
    filters.observedAt = overviewData.default_observed_at || dateData.items[dateData.items.length - 1];
    await loadMap(false);
  } catch (currentError) {
    error.value = getOverviewApiErrorMessage(
      currentError,
      getApiErrorMessage(currentError, '首页总览加载失败。'),
    );
  } finally {
    loading.value = false;
  }
}

async function loadMap(manageLoading = true) {
  if (!filters.metricCode) {
    return;
  }
  const requestId = ++mapRequestId;
  if (manageLoading) {
    loading.value = true;
  }
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
    const selected = selectedPlotId.value
      ? featureCollection.value.features.find((feature) => feature.properties.plot_id === selectedPlotId.value)
      : featureCollection.value.features[0];
    if (selected?.properties.plot_id) {
      await handlePlotClick(selected.properties);
    }
  } catch (currentError) {
    if (requestId === mapRequestId) {
      error.value = getApiErrorMessage(currentError, '首页地图图层加载失败，请检查 /api/map/layers。');
    }
  } finally {
    if (manageLoading && requestId === mapRequestId) {
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
      error.value = getApiErrorMessage(currentError, '地块画像或趋势加载失败。');
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

function metricSnapshot(kind: 'ndvi' | 'soil' | 'weather') {
  const observations = summary.value?.latest_observations ?? [];
  const matcher = {
    ndvi: (name: string, code: string) => code.includes('ndvi') || name.includes('NDVI') || name.includes('长势'),
    soil: (name: string, code: string) => code.includes('soil') || name.includes('土壤') || name.includes('含水'),
    weather: (name: string, code: string) => code.includes('weather') || name.includes('气温') || name.includes('降雨') || name.includes('气象'),
  }[kind];
  const item = observations.find((observation) =>
    matcher(observation.metric_name, observation.metric_code.toLowerCase()),
  );
  return item ? formatMetricValue(item.value, item.unit) : '--';
}

function formatMetricValue(value: MapFeatureProperties['value'], unit?: string | null) {
  if (value === null || value === undefined || value === '') {
    return '--';
  }
  return `${value}${unit ? ` ${unit}` : ''}`;
}

function getPlotName(properties: MapFeatureProperties | undefined) {
  return properties?.plot_name || properties?.region || '东林村-01';
}

function getCropType(properties: MapFeatureProperties | undefined) {
  return properties?.region?.includes('二') ? '再生稻' : '早稻';
}

function getPlotArea(properties: MapFeatureProperties | undefined) {
  const code = properties?.plot_code || properties?.plot_id || '';
  const seed = Array.from(code).reduce((sum, char) => sum + char.charCodeAt(0), 0);
  const area = 28 + (seed % 18) + ((seed % 7) / 10);
  return `${area.toFixed(1)} ha`;
}

function getHealthScore(properties: MapFeatureProperties | undefined) {
  const rawValue = Number(properties?.value);
  if (Number.isFinite(rawValue)) {
    const normalized = rawValue <= 1 ? rawValue * 100 : rawValue;
    return Math.round(Math.min(Math.max(normalized, 0), 100));
  }
  const flag = properties?.quality_flag || properties?.status;
  if (flag === 'missing') {
    return 68;
  }
  if (flag === 'outlier' || flag === 'error') {
    return 61;
  }
  return overview.value?.health_score ?? 82;
}

function buildLineOption(dates: string[], values: number[], name: string, color: string): EChartsOption {
  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 22, right: 18, bottom: 30, left: 38 },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#eaecf0' } },
      axisLabel: { color: '#667085', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f2f4f7' } },
      axisLabel: { color: '#667085', fontSize: 11 },
    },
    series: [{
      name,
      type: 'line',
      smooth: true,
      symbolSize: 6,
      data: values,
      lineStyle: { width: 2.5, color },
      itemStyle: { color },
      areaStyle: { color: `${color}18` },
    }],
  };
}
</script>

<style scoped>
.overview-workbench {
  display: grid;
  gap: 14px;
}

.overview-command-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: var(--rf-surface);
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 650;
  padding: 0 12px;
  text-decoration: none;
}

.overview-command-link:hover {
  border-color: color-mix(in srgb, var(--rf-primary) 34%, var(--rf-border));
  color: var(--rf-primary);
}

.mission-control {
  position: relative;
  display: grid;
  grid-template-columns: minmax(720px, 1fr) 340px;
  gap: 14px;
  align-items: start;
}

.workbench-rail {
  position: absolute;
  top: 72px;
  left: 18px;
  z-index: 6;
  display: grid;
  gap: 10px;
  width: 238px;
  max-height: 590px;
  overflow: auto;
  padding-right: 2px;
}

.workbench-panel {
  min-width: 0;
  border: 1px solid var(--rf-border-soft);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--rf-shadow-xs);
  padding: 13px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.panel-heading h2,
.panel-heading h3 {
  margin: 0;
  color: var(--rf-text);
  font-size: 14px;
  font-weight: 780;
  line-height: 1.35;
}

.panel-heading h3 {
  font-size: 13px;
}

.panel-heading p,
.panel-heading span {
  margin: 3px 0 0;
  color: var(--rf-text-muted);
  font-size: 11px;
}

.panel-heading--compact {
  align-items: center;
  margin-bottom: 8px;
}

.panel-action,
.plot-search button {
  min-height: 30px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 10px;
  background: #fff;
  color: var(--rf-text);
  cursor: pointer;
  font-size: 12px;
  font-weight: 650;
  padding: 0 10px;
}

.plot-panel {
  display: grid;
  gap: 10px;
}

.plot-search {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
}

.plot-search input {
  height: 34px;
  min-width: 0;
  border: 1px solid var(--rf-border-soft);
  border-radius: 10px;
  background: #fff;
  color: var(--rf-text);
  font-size: 12px;
  padding: 0 10px;
  box-shadow: none;
  outline: none;
}

.plot-search input:focus {
  border-color: color-mix(in srgb, var(--rf-primary) 42%, var(--rf-border));
  box-shadow: 0 0 0 2px rgba(8, 116, 67, 0.1);
}

.plot-list,
.layer-list,
.batch-panel ul,
.event-panel ul,
.risk-panel ul,
.advice-panel ul,
.inspector-placeholder ul {
  display: grid;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.plot-list__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 50px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  padding: 8px;
  text-align: left;
  transition:
    background-color 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.plot-list__item:hover,
.plot-list__item.is-active {
  border-color: color-mix(in srgb, var(--rf-primary) 22%, var(--rf-border-soft));
  background: color-mix(in srgb, var(--rf-primary-soft) 72%, white);
  box-shadow: var(--rf-shadow-xs);
}

.plot-list__item span {
  display: grid;
  grid-template-columns: auto 1fr;
  column-gap: 8px;
  min-width: 0;
}

.plot-list__item i {
  grid-row: span 2;
  align-self: center;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--rf-primary);
}

.plot-list__item strong,
.plot-list__item b {
  overflow: hidden;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 760;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plot-list__item small {
  color: var(--rf-text-muted);
  font-size: 11px;
}

.plot-list__item b {
  display: grid;
  justify-items: end;
  color: var(--rf-primary-dark);
}

.plot-list__item b small {
  margin-bottom: 2px;
  color: var(--rf-text-soft);
  font-weight: 600;
}

.panel-foot {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--rf-border-soft);
  color: var(--rf-text-muted);
  font-size: 11px;
  padding-top: 8px;
}

.layer-list label {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  min-height: 28px;
  color: var(--rf-text);
  font-size: 12px;
  font-weight: 650;
}

.layer-list span {
  border-radius: 999px;
  background: var(--rf-bg-subtle);
  color: var(--rf-text-muted);
  font-size: 10px;
  padding: 2px 7px;
}

.opacity-control {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  border-top: 1px solid var(--rf-border-soft);
  margin-top: 8px;
  padding-top: 9px;
  color: var(--rf-text-muted);
  font-size: 11px;
}

.opacity-control input {
  accent-color: var(--rf-primary);
}

.opacity-control b {
  color: var(--rf-text);
}

.scenario-panel,
.phase-panel {
  display: grid;
  gap: 10px;
}

.scenario-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.scenario-tabs button {
  min-height: 28px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: #fff;
  color: var(--rf-text-muted);
  cursor: pointer;
  font-size: 11px;
  font-weight: 650;
  padding: 0 8px;
}

.scenario-tabs button.is-active {
  border-color: color-mix(in srgb, var(--rf-primary) 30%, var(--rf-border-soft));
  background: var(--rf-primary-soft);
  color: var(--rf-primary-dark);
}

.source-list {
  display: grid;
  gap: 5px;
}

.source-list span {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: var(--rf-text-muted);
  font-size: 11px;
}

.source-list i {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--rf-success);
}

.source-list b {
  margin-left: auto;
  color: var(--rf-primary-dark);
}

.compact-timeline {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0;
  margin: 2px 0 0;
  padding: 0;
  list-style: none;
}

.compact-timeline li {
  position: relative;
  color: var(--rf-text-soft);
  font-size: 10px;
  text-align: center;
}

.compact-timeline li::before {
  content: "";
  display: block;
  width: 8px;
  height: 8px;
  margin: 0 auto 5px;
  border: 2px solid var(--rf-border);
  border-radius: 999px;
  background: #fff;
}

.compact-timeline li::after {
  content: "";
  position: absolute;
  top: 4px;
  right: 50%;
  width: 100%;
  height: 1px;
  background: var(--rf-border-soft);
  z-index: -1;
}

.compact-timeline li:first-child::after {
  display: none;
}

.compact-timeline li.is-active {
  color: var(--rf-primary-dark);
  font-weight: 800;
}

.compact-timeline li.is-active::before {
  border-color: var(--rf-primary);
  background: var(--rf-primary);
  box-shadow: 0 0 0 4px var(--rf-primary-soft);
}

.phase-meta {
  display: flex;
  justify-content: space-between;
  color: var(--rf-text-muted);
  font-size: 10px;
}

.map-workspace {
  position: relative;
  min-width: 0;
}

.map-workspace :deep(.map-panel) {
  height: 100%;
}

.map-workspace :deep(.map-panel__canvas) {
  min-height: 680px !important;
}

.map-statusbar {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 4;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  max-width: 48%;
}

.map-statusbar span,
.map-statusbar button,
.map-statusbar a {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 34px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--rf-shadow-xs);
  color: var(--rf-text);
  cursor: pointer;
  font-size: 12px;
  font-weight: 650;
  text-decoration: none;
  padding: 0 10px;
  backdrop-filter: blur(16px);
}

.map-statusbar button {
  font-family: inherit;
}

.dot-good,
.dot-warning,
.dot-teal {
  width: 7px;
  height: 7px;
  border-radius: 999px;
}

.dot-good {
  background: var(--rf-success);
}

.dot-warning {
  background: var(--rf-warning);
}

.dot-teal {
  background: var(--rf-teal);
}

.map-points {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
}

.map-point {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 3px solid #fff;
  border-radius: 999px;
  box-shadow: 0 8px 18px rgba(16, 24, 40, 0.18);
}

.map-point--sensor {
  background: var(--rf-teal);
}

.map-point--warning {
  background: var(--rf-warning);
}

.map-point--a {
  top: 24%;
  left: 65%;
}

.map-point--b {
  top: 45%;
  left: 30%;
}

.map-point--c {
  top: 70%;
  left: 72%;
}

.map-compass {
  position: absolute;
  right: 18px;
  bottom: 18px;
  z-index: 4;
  display: grid;
  width: 62px;
  height: 62px;
  place-items: center;
  border: 2px solid rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  color: #fff;
  text-shadow: 0 1px 4px rgba(16, 24, 40, 0.4);
}

.map-compass b {
  position: absolute;
  top: -14px;
  font-size: 12px;
}

.map-compass span {
  width: 2px;
  height: 42px;
  background: linear-gradient(180deg, #fff 0 45%, transparent 45% 55%, #fff 55%);
  transform: rotate(26deg);
}

.map-legend-card {
  display: grid;
  gap: 8px;
  min-width: 146px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--rf-shadow-soft);
  padding: 10px;
  backdrop-filter: blur(16px);
}

.map-legend-card strong,
.map-legend-card span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--rf-text);
  font-size: 11px;
}

.map-legend-card i {
  width: 12px;
  height: 12px;
  border-radius: 5px;
}

.legend-good {
  background: var(--rf-success);
}

.legend-warning {
  background: var(--rf-warning);
}

.legend-teal {
  background: var(--rf-teal);
}

.plot-inspector {
  min-width: 0;
  max-height: 680px;
  overflow: auto;
  padding-right: 2px;
}

.plot-profile-card {
  display: grid;
  gap: 12px;
}

.inspector-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.inspector-head span {
  color: var(--rf-text-muted);
  font-size: 11px;
  font-weight: 650;
}

.inspector-head h2 {
  margin: 3px 0 0;
  color: var(--rf-text);
  font-size: 18px;
  font-weight: 820;
  line-height: 1.2;
}

.inspector-actions {
  display: flex;
  gap: 4px;
}

.inspector-actions button {
  width: 30px;
  height: 30px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--rf-text-muted);
  cursor: pointer;
  font-size: 18px;
}

.plot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.plot-tags > span {
  border-radius: 999px;
  background: var(--rf-bg-subtle);
  color: var(--rf-text-muted);
  font-size: 11px;
  font-weight: 650;
  padding: 4px 8px;
}

.inspector-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-bottom: 1px solid var(--rf-border-soft);
}

.inspector-tabs button {
  min-height: 34px;
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--rf-text-muted);
  cursor: pointer;
  font-size: 12px;
  font-weight: 720;
}

.inspector-tabs button.is-active {
  border-color: var(--rf-primary);
  color: var(--rf-primary-dark);
}

.stage-card {
  display: grid;
  gap: 12px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 14px;
  background: var(--rf-surface-muted);
  padding: 12px;
}

.stage-card__copy span,
.stage-card__copy small,
.inspector-metric span,
.inspector-metric small {
  display: block;
  color: var(--rf-text-muted);
  font-size: 11px;
  line-height: 1.45;
}

.stage-card__copy strong {
  display: block;
  margin-top: 5px;
  color: var(--rf-text);
  font-size: 17px;
  font-weight: 820;
}

.stage-track {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.stage-track li {
  display: grid;
  gap: 4px;
  color: var(--rf-text-soft);
  font-size: 10px;
  text-align: center;
}

.stage-track li::before {
  content: "";
  width: 8px;
  height: 8px;
  margin: 0 auto;
  border: 2px solid var(--rf-border);
  border-radius: 999px;
  background: #fff;
}

.stage-track li.is-active {
  color: var(--rf-primary-dark);
  font-weight: 800;
}

.stage-track li.is-active::before {
  border-color: var(--rf-primary);
  background: var(--rf-primary);
}

.inspector-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.inspector-metric {
  min-width: 0;
  border: 1px solid var(--rf-border-soft);
  border-radius: 14px;
  background: #fff;
  box-shadow: var(--rf-shadow-xs);
  padding: 12px;
}

.inspector-metric strong {
  display: inline-block;
  margin-top: 6px;
  color: var(--rf-text);
  font-size: 22px;
  font-weight: 840;
  line-height: 1.08;
}

.inspector-metric--score strong {
  color: var(--rf-primary);
}

.risk-panel,
.advice-panel,
.inspector-placeholder {
  border: 1px solid var(--rf-border-soft);
  border-radius: 14px;
  background: var(--rf-surface-muted);
  padding: 12px;
}

.risk-panel {
  background: color-mix(in srgb, var(--rf-error-soft) 54%, white);
}

.risk-panel li,
.advice-panel li,
.inspector-placeholder li,
.inspector-placeholder span {
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.55;
}

.advice-panel footer {
  margin-top: 8px;
  color: var(--rf-text-soft);
  font-size: 10px;
  text-align: right;
}

.inspector-placeholder {
  display: grid;
  gap: 10px;
}

.inspector-placeholder strong {
  color: var(--rf-text);
  font-size: 15px;
}

.analysis-dock {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) minmax(300px, 1fr) minmax(260px, 0.72fr) minmax(260px, 0.72fr);
  gap: 14px;
  align-items: stretch;
}

.analysis-dock :deep(.chart-card) {
  border-radius: 16px;
}

.batch-panel li,
.event-panel li {
  display: grid;
  gap: 2px;
  border-bottom: 1px solid var(--rf-border-soft);
  padding-bottom: 7px;
}

.batch-panel li:last-child,
.event-panel li:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.batch-panel strong,
.event-panel strong {
  overflow: hidden;
  color: var(--rf-text);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.batch-panel span,
.event-panel span {
  color: var(--rf-text-muted);
  font-size: 11px;
}

@media (max-width: 1500px) {
  .mission-control {
    grid-template-columns: minmax(680px, 1fr) 320px;
  }
}

@media (max-width: 1120px) {
  .mission-control,
  .analysis-dock {
    grid-template-columns: 1fr;
  }

  .map-workspace :deep(.map-panel__canvas) {
    min-height: 560px !important;
  }

  .workbench-rail {
    order: 3;
    position: static;
    width: auto;
    max-height: none;
    overflow: visible;
  }

  .map-workspace {
    order: 1;
  }

  .plot-inspector {
    order: 2;
    max-height: none;
    overflow: visible;
  }
}

@media (max-width: 760px) {
  .inspector-grid,
  .stage-track,
  .compact-timeline {
    grid-template-columns: 1fr;
  }

  .map-statusbar {
    left: 12px;
    right: 12px;
    max-width: none;
  }
}
</style>
