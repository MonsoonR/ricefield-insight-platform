<template>
  <PageContainer>
    <div class="warning-stat-grid">
      <StatCard label="预警总数" :value="summary.total" :note="summary.totalNote" :icon="SafetyCertificateOutlined" tone="green" />
      <StatCard label="严重预警" :value="summary.critical" :note="summary.criticalNote" :icon="WarningOutlined" tone="red" />
      <StatCard label="受影响地块" :value="summary.plotCount" :note="summary.plotNote" :icon="EnvironmentOutlined" tone="yellow" />
      <StatCard label="受影响指标" :value="summary.metricCount" :note="summary.metricNote" :icon="ExperimentOutlined" tone="blue" />
      <StatCard label="最新预警时间" :value="summary.latestDate" :note="summary.latestNote" :icon="CalendarOutlined" tone="purple" />
    </div>

    <FilterBar>
      <div class="filter-field">
        <span>指标</span>
        <MetricSelector v-model="filters.metricCode" :options="metricOptions" placeholder="全部指标" />
      </div>
      <div class="filter-field">
        <span>区域</span>
        <RegionSelector v-model="filters.region" />
      </div>
      <div class="filter-field">
        <span>预警类型</span>
        <SelectControl
          v-model="filters.warningCategory"
          :options="warningCategoryOptions"
          :allow-empty="false"
        />
      </div>
      <div class="filter-field">
        <span>严重程度</span>
        <SelectControl
          v-model="filters.severityLevel"
          :options="severityOptions"
          :allow-empty="false"
        />
      </div>
      <div class="filter-field filter-field--range">
        <span>日期范围</span>
        <DateRangeSelector v-model="filters.dateRange" />
      </div>
      <div class="filter-actions">
        <a-button type="primary" :loading="loading" @click="loadWarnings">
          <template #icon><SearchOutlined /></template>
          查询
        </a-button>
        <a-button :disabled="loading" @click="resetFilters">
          <template #icon><ReloadOutlined /></template>
          重置
        </a-button>
      </div>
    </FilterBar>

    <ErrorState v-if="error" :message="error" compact />

    <div class="risk-center">
      <div class="risk-distribution">
        <ChartCard
          title="预警类型分布"
          description="数据质量、农情状态与趋势变化分类。"
          :loading="loading"
          :empty="filteredWarnings.length === 0"
          empty-text="当前筛选条件下暂无预警"
          :height="232"
        >
          <div class="distribution-chart">
            <EChartView :option="typeDistributionOption" :height="164" />
            <div class="distribution-legend">
              <div v-for="entry in typeDistribution" :key="entry.name" class="distribution-legend__item">
                <span><i :style="{ backgroundColor: entry.itemStyle.color }" />{{ entry.name }}</span>
                <strong>{{ entry.value }} 条</strong>
                <em>{{ percent(entry.value, filteredWarnings.length) }}%</em>
              </div>
            </div>
          </div>
        </ChartCard>
        <ChartCard
          title="严重程度分布"
          description="关注、预警、严重三类风险等级。"
          :loading="loading"
          :empty="filteredWarnings.length === 0"
          empty-text="当前筛选条件下暂无预警"
          :height="232"
        >
          <div class="distribution-chart">
            <EChartView :option="severityDistributionOption" :height="164" />
            <div class="distribution-legend">
              <div v-for="entry in severityDistribution" :key="entry.name" class="distribution-legend__item">
                <span><i :style="{ backgroundColor: entry.itemStyle.color }" />{{ entry.name }}</span>
                <strong>{{ entry.value }} 条</strong>
                <em>{{ percent(entry.value, filteredWarnings.length) }}%</em>
              </div>
            </div>
          </div>
        </ChartCard>
      </div>

      <CesiumMapPanel
        title="预警地块分布"
        :feature-collection="warningFeatureCollection"
        :height="522"
        :loading="loading"
        :selected-plot-id="selectedPlotId"
        tight-view
        @plot-click="handlePlotClick"
      >
        <template #legend>
          <div class="warning-legend">
            <strong>图例</strong>
            <span><i class="legend-critical" />严重</span>
            <span><i class="legend-warning" />预警</span>
            <span><i class="legend-watch" />关注</span>
            <span><i class="legend-normal" />正常</span>
            <span><i class="legend-empty" />无数据</span>
          </div>
        </template>
      </CesiumMapPanel>

      <section class="panel latest-warning-panel">
        <header>
          <div>
            <h2 class="section-title">最新预警</h2>
            <p class="section-subtitle">最近 {{ latestWarnings.length }} 条风险事件</p>
          </div>
          <a-button type="link" size="small" @click="scrollToTable">查看更多</a-button>
        </header>
        <EmptyState v-if="latestWarnings.length === 0" compact description="当前筛选条件下暂无预警" />
        <div v-else class="latest-warning-list">
          <button
            v-for="item in latestWarnings"
            :key="item.warning_id"
            type="button"
            class="latest-warning-item"
            :class="{ 'latest-warning-item--active': item.warning_id === selectedWarningId }"
            @click="selectWarning(item)"
          >
            <StatusTag :status="displayStatus(item)" />
            <span class="latest-warning-item__title">{{ warningTitle(item) }}</span>
            <small>{{ item.observed_at }}</small>
            <em>{{ item.plot_code }} · {{ item.region || '未分区' }}</em>
          </button>
        </div>
      </section>
    </div>

    <DataTable
      ref="tableRef"
      title="预警明细列表"
      description="预警描述和建议措施为前端语义转换，需结合田间记录综合判断。"
      :columns="columns"
      :data-source="tableRows"
      :loading="loading"
      row-key="warning_id"
      :row-class-name="rowClassName"
      :pagination="{ pageSize: 10, showSizeChanger: false, showTotal: (total: number) => `共 ${total} 条` }"
      :scroll="{ x: 1520 }"
      empty-text="当前筛选条件下暂无预警"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'warning_category'">
          {{ categoryLabel(record.warning_category as string) }}
        </template>
        <template v-else-if="column.key === 'severity_level'">
          <StatusTag :status="record.severity_level as string" />
        </template>
        <template v-else-if="column.key === 'description'">
          <a-tooltip :title="record.description as string">
            <span class="ellipsis-text">{{ record.description }}</span>
          </a-tooltip>
        </template>
        <template v-else-if="column.key === 'suggestion'">
          <a-tooltip :title="record.suggestion as string">
            <span class="ellipsis-text">{{ record.suggestion }}</span>
          </a-tooltip>
        </template>
        <template v-else-if="column.key === 'actions'">
          <div class="table-actions">
            <a-button size="small" @click="goPlotDetail(record.plot_id as string)">查看画像</a-button>
            <a-button size="small" @click="goMapTwin(record.plot_id as string)">定位地图</a-button>
          </div>
        </template>
      </template>
    </DataTable>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  CalendarOutlined,
  EnvironmentOutlined,
  ExperimentOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
  SearchOutlined,
  WarningOutlined,
} from '@ant-design/icons-vue';
import type { EChartsOption } from 'echarts';
import { computed, nextTick, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  fetchMapLayers,
  fetchMetrics,
  fetchWarnings,
  getApiErrorMessage,
} from '@/api';
import {
  CesiumMapPanel,
  ChartCard,
  DataTable,
  DateRangeSelector,
  EChartView,
  EmptyState,
  ErrorState,
  FilterBar,
  MetricSelector,
  PageContainer,
  RegionSelector,
  SelectControl,
  StatCard,
  StatusTag,
} from '@/components/base';
import { buildMapTwinLocation, buildPlotDetailRequestPlan } from '@/services/pageLinkage';
import type {
  MapFeatureCollection,
  MapFeatureProperties,
  Metric,
  RegionCode,
  WarningItem,
} from '@/types/api';
import type { TableColumnsType } from '@/types/table';
import type { StatusLevel } from '@/utils/status';

type WarningCategory = 'all' | 'data_quality' | 'agronomy' | 'trend';
type SeverityFilter = 'all' | 'watch' | 'warning' | 'critical';

type WarningRow = WarningItem & {
  warning_category: Exclude<WarningCategory, 'all'>;
  severity_level: StatusLevel;
  description: string;
  suggestion: string;
};

const STATUS_COLORS: Record<StatusLevel, string> = {
  normal: '#16A36A',
  watch: '#C58B04',
  warning: '#EA580C',
  critical: '#DC2626',
  empty: '#6B7280',
};

const router = useRouter();
const loading = ref(false);
const error = ref('');
const metrics = ref<Metric[]>([]);
const warnings = ref<WarningItem[]>([]);
const baseFeatureCollection = ref<MapFeatureCollection>({ type: 'FeatureCollection', features: [] });
const selectedPlotId = ref('');
const selectedWarningId = ref('');
const tableRef = ref<InstanceType<typeof DataTable>>();
const filters = reactive<{
  region: RegionCode;
  metricCode?: string;
  warningCategory: WarningCategory;
  severityLevel: SeverityFilter;
  dateRange?: [string, string];
}>({
  region: 'all',
  metricCode: undefined,
  warningCategory: 'all',
  severityLevel: 'all',
  dateRange: undefined,
});

const warningCategoryOptions = [
  { label: '全部类型', value: 'all' },
  { label: '数据质量预警', value: 'data_quality' },
  { label: '农情状态预警', value: 'agronomy' },
  { label: '趋势变化预警', value: 'trend' },
];
const severityOptions = [
  { label: '全部', value: 'all' },
  { label: '关注', value: 'watch' },
  { label: '预警', value: 'warning' },
  { label: '严重', value: 'critical' },
];
const metricOptions = computed(() => [
  { label: '全部指标', value: '' },
  ...metrics.value.map((item) => ({ label: item.metric_name, value: item.metric_code })),
]);
const normalizedMetricCode = computed(() => filters.metricCode || undefined);
const tableRows = computed<WarningRow[]>(() =>
  [...warnings.value]
    .sort((a, b) => b.observed_at.localeCompare(a.observed_at) || a.plot_code.localeCompare(b.plot_code))
    .map((item) => ({
      ...item,
      warning_category: warningCategory(item),
      severity_level: severityLevel(item),
      description: warningDescription(item),
      suggestion: warningSuggestion(item),
    })),
);
const filteredWarnings = computed(() =>
  tableRows.value.filter((item) =>
    (filters.warningCategory === 'all' || item.warning_category === filters.warningCategory)
    && (filters.severityLevel === 'all' || item.severity_level === filters.severityLevel),
  ),
);
const latestWarnings = computed(() => filteredWarnings.value.slice(0, 5));
const summary = computed(() => {
  const critical = filteredWarnings.value.filter((item) => item.severity_level === 'critical').length;
  const plotIds = new Set(filteredWarnings.value.map((item) => item.plot_id));
  const metricCodes = new Set(filteredWarnings.value.map((item) => item.metric_code));
  const latest = filteredWarnings.value[0];
  const previousTotal = warnings.value.length;
  return {
    total: filteredWarnings.value.length,
    totalNote: previousTotal ? `当前筛选范围，共 ${previousTotal} 条原始预警` : '当前筛选范围',
    critical,
    criticalNote: critical ? '需要优先复核' : '暂无严重事件',
    plotCount: plotIds.size,
    plotNote: filteredWarnings.value.length ? `占预警数 ${percent(plotIds.size, filteredWarnings.value.length)}%` : '暂无受影响地块',
    metricCount: metricCodes.size,
    metricNote: metrics.value.length ? `占指标总数 ${percent(metricCodes.size, metrics.value.length)}%` : '当前筛选指标',
    latestDate: latest?.observed_at ?? '--',
    latestNote: latest ? warningTitle(latest) : '暂无最新预警',
  };
});
const typeDistribution = computed(() =>
  (['data_quality', 'agronomy', 'trend'] as const).map((category) => {
    const count = filteredWarnings.value.filter((item) => item.warning_category === category).length;
    return {
      name: categoryLabel(category),
      value: count,
      itemStyle: { color: categoryColor(category) },
    };
  }),
);
const severityDistribution = computed(() =>
  (['critical', 'warning', 'watch'] as const).map((level) => {
    const count = filteredWarnings.value.filter((item) => item.severity_level === level).length;
    return {
      name: severityLabel(level),
      value: count,
      itemStyle: { color: STATUS_COLORS[level] },
    };
  }),
);
const warningFeatureCollection = computed<MapFeatureCollection>(() => {
  const warningsByPlot = new Map<string, WarningRow[]>();
  filteredWarnings.value.forEach((item) => {
    warningsByPlot.set(item.plot_id, [...(warningsByPlot.get(item.plot_id) ?? []), item]);
  });

  return {
    type: 'FeatureCollection',
    features: baseFeatureCollection.value.features.map((feature) => {
      const plotWarnings = warningsByPlot.get(feature.properties.plot_id || '') ?? [];
      const worstLevel = worstSeverity(plotWarnings);
      return {
        ...feature,
        properties: {
          ...feature.properties,
          value: plotWarnings.length || 1,
          quality_flag: mapSeverityToMapFlag(worstLevel),
          fill_color: statusColorForMap(worstLevel),
        },
      };
    }),
  };
});
const typeDistributionOption = computed<EChartsOption>(() => buildDonutOption(
  typeDistribution.value,
  filteredWarnings.value.length,
  '总预警',
));
const severityDistributionOption = computed<EChartsOption>(() => buildDonutOption(
  severityDistribution.value,
  filteredWarnings.value.length,
  '总预警',
));

const columns: TableColumnsType = [
  { title: '日期', dataIndex: 'observed_at', key: 'observed_at', width: 112 },
  { title: '地块编号', dataIndex: 'plot_code', key: 'plot_code', width: 94 },
  { title: '地块名称', dataIndex: 'plot_name', key: 'plot_name', width: 140 },
  { title: '区域', dataIndex: 'region', key: 'region', width: 100 },
  { title: '指标', dataIndex: 'metric_name', key: 'metric_name', width: 140 },
  { title: '预警类型', dataIndex: 'warning_category', key: 'warning_category', width: 126 },
  { title: '严重程度', dataIndex: 'severity_level', key: 'severity_level', width: 100 },
  { title: '预警描述', dataIndex: 'description', key: 'description', width: 210 },
  { title: '建议措施', dataIndex: 'suggestion', key: 'suggestion', width: 230 },
  { title: '操作', key: 'actions', width: 150 },
];

onMounted(async () => {
  await initialize();
});

async function initialize() {
  loading.value = true;
  try {
    const metricData = await fetchMetrics();
    metrics.value = metricData.items;
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '预警分析基础数据加载失败。');
  } finally {
    loading.value = false;
  }
  await loadWarnings();
}

async function loadWarnings() {
  loading.value = true;
  error.value = '';
  try {
    const [warningData, layerData] = await Promise.all([
      fetchWarnings({
        region: filters.region,
        metricCode: normalizedMetricCode.value,
        startDate: filters.dateRange?.[0],
        endDate: filters.dateRange?.[1],
      }),
      fetchMapLayers({ region: filters.region }),
    ]);
    warnings.value = warningData.items;
    baseFeatureCollection.value = layerData.layers[0]?.feature_collection ?? { type: 'FeatureCollection', features: [] };
    selectedWarningId.value = filteredWarnings.value[0]?.warning_id ?? '';
    selectedPlotId.value = filteredWarnings.value[0]?.plot_id ?? '';
  } catch (currentError) {
    warnings.value = [];
    baseFeatureCollection.value = { type: 'FeatureCollection', features: [] };
    error.value = getApiErrorMessage(currentError, 'API 请求失败，请稍后重试。');
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.region = 'all';
  filters.metricCode = undefined;
  filters.warningCategory = 'all';
  filters.severityLevel = 'all';
  filters.dateRange = undefined;
  void loadWarnings();
}

function handlePlotClick(properties: MapFeatureProperties) {
  selectedPlotId.value = properties.plot_id ?? '';
  const match = filteredWarnings.value.find((item) => item.plot_id === selectedPlotId.value);
  selectedWarningId.value = match?.warning_id ?? '';
  if (match) {
    void scrollToTable();
  }
}

function selectWarning(item: WarningRow) {
  selectedWarningId.value = item.warning_id;
  selectedPlotId.value = item.plot_id;
  void scrollToTable();
}

async function scrollToTable() {
  await nextTick();
  const element = tableRef.value?.$el as HTMLElement | undefined;
  element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function goPlotDetail(plotId: string) {
  const plan = buildPlotDetailRequestPlan(plotId);
  if (plan) {
    void router.push(plan.routeLocation);
  }
}

function goMapTwin(plotId: string) {
  void router.push(buildMapTwinLocation(plotId));
}

function rowClassName(record: object) {
  return (record as WarningRow).warning_id === selectedWarningId.value ? 'warning-row--active' : '';
}

function warningCategory(item: WarningItem): Exclude<WarningCategory, 'all'> {
  if (item.warning_type === 'missing') {
    return 'data_quality';
  }
  if (item.metric_code === 'leaf_area_index' || item.metric_code === 'plant_height') {
    return 'trend';
  }
  return 'agronomy';
}

function severityLevel(item: WarningItem): StatusLevel {
  if (item.warning_type === 'error' || item.severity === 'error') {
    return 'critical';
  }
  if (item.warning_type === 'outlier') {
    return 'warning';
  }
  return 'watch';
}

function displayStatus(item: WarningRow | WarningItem) {
  return 'severity_level' in item ? item.severity_level : severityLevel(item);
}

function warningTitle(item: WarningRow | WarningItem) {
  return `${item.metric_name} ${shortRiskText(item)}`;
}

function shortRiskText(item: WarningRow | WarningItem) {
  if (item.warning_type === 'missing') {
    return '存在观测缺失';
  }
  if (item.metric_code === 'ph') {
    return Number(item.value) >= 7.5 ? '轻微偏高' : '轻微偏低';
  }
  if (item.metric_code === 'leaf_area_index') {
    return '观测值波动较大';
  }
  if (item.metric_code === 'chlorophyll') {
    return '异常偏低';
  }
  if (item.metric_code === 'nitrogen') {
    return '轻微偏低';
  }
  if (item.warning_type === 'outlier' || item.warning_type === 'error') {
    return '观测异常';
  }
  return '需要关注';
}

function warningDescription(item: WarningItem) {
  const valueText = item.value === null || item.value === undefined ? '暂无有效观测值' : `当前值 ${item.value}`;
  if (item.warning_type === 'missing') {
    return `${item.plot_code} 当前地块存在观测缺失，需确认采集链路和观测记录。`;
  }
  if (item.metric_code === 'ph') {
    return `${item.plot_code} 的 pH ${shortRiskText(item)}，${valueText}，建议结合历史范围复核。`;
  }
  if (item.metric_code === 'leaf_area_index') {
    return `${item.plot_code} 的 LAI 近期波动较大，${valueText}，需要持续观察后续变化。`;
  }
  return `${item.plot_code} 的${item.metric_name}${shortRiskText(item)}，${valueText}，建议复核田间观测情况。`;
}

function warningSuggestion(item: WarningItem) {
  if (item.warning_type === 'missing') {
    return '建议检查数据采集链路是否存在缺失，并补充或复核对应观测记录。';
  }
  if (item.metric_code === 'nitrogen' || item.metric_code === 'chlorophyll') {
    return '建议结合灌溉、施肥和田间管理记录综合判断，避免仅凭单次观测下结论。';
  }
  if (item.metric_code === 'leaf_area_index') {
    return '建议持续关注后续观测变化，并复核近期图像或传感器采集稳定性。';
  }
  return '建议复核田间观测情况，并结合历史趋势和管理记录综合判断。';
}

function categoryLabel(category: string) {
  const labels: Record<string, string> = {
    data_quality: '数据质量预警',
    agronomy: '农情状态预警',
    trend: '趋势变化预警',
  };
  return labels[category] ?? category;
}

function categoryColor(category: string) {
  const colors: Record<string, string> = {
    data_quality: '#2878D7',
    agronomy: STATUS_COLORS.normal,
    trend: STATUS_COLORS.warning,
  };
  return colors[category] ?? STATUS_COLORS.empty;
}

function severityLabel(level: StatusLevel) {
  const labels: Record<StatusLevel, string> = {
    normal: '正常',
    watch: '关注',
    warning: '预警',
    critical: '严重',
    empty: '无数据',
  };
  return labels[level];
}

function worstSeverity(items: WarningRow[]): StatusLevel {
  if (items.some((item) => item.severity_level === 'critical')) {
    return 'critical';
  }
  if (items.some((item) => item.severity_level === 'warning')) {
    return 'warning';
  }
  if (items.some((item) => item.severity_level === 'watch')) {
    return 'watch';
  }
  return 'normal';
}

function statusColorForMap(level: StatusLevel) {
  if (level === 'normal') {
    return STATUS_COLORS.normal;
  }
  if (level === 'empty') {
    return '#D1D5DB';
  }
  return STATUS_COLORS[level];
}

function mapSeverityToMapFlag(level: StatusLevel) {
  if (level === 'critical' || level === 'warning') {
    return 'outlier';
  }
  return 'normal';
}

function buildDonutOption(data: Array<{ name: string; value: number; itemStyle: { color: string } }>, total: number, subtext: string): EChartsOption {
  return {
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const item = params as { name?: string; value?: number };
        return `${item.name}：${item.value ?? 0} 条（${percent(item.value ?? 0, total)}%）`;
      },
    },
    title: {
      text: String(total),
      subtext,
      left: '50%',
      top: '40%',
      textAlign: 'center',
      textStyle: { color: '#1F2937', fontSize: 24, fontWeight: 800 },
      subtextStyle: { color: '#6B7280', fontSize: 12 },
    },
    legend: { show: false },
    series: [{
      type: 'pie',
      radius: ['54%', '78%'],
      center: ['50%', '50%'],
      label: { show: false },
      data,
    }],
  };
}

function percent(value: number, total: number) {
  if (!total) {
    return 0;
  }
  return Math.round((value / total) * 1000) / 10;
}
</script>

<style scoped>
.warning-stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.filter-field {
  display: grid;
  gap: 6px;
  min-width: 172px;
}

.filter-field--range {
  min-width: 250px;
}

.filter-field span {
  color: var(--rf-text-muted);
  font-size: 12px;
  font-weight: 700;
}

.filter-actions {
  display: flex;
  align-self: end;
  gap: 10px;
}

.filter-actions .ant-btn {
  min-width: 86px;
}

.risk-center {
  display: grid;
  grid-template-columns: 300px minmax(0, 1.5fr) 340px;
  gap: 16px;
}

.risk-distribution {
  display: grid;
  gap: 16px;
}

.distribution-chart {
  display: grid;
  gap: 8px;
}

.distribution-legend {
  display: grid;
  gap: 7px;
  border-top: 1px solid var(--rf-border-soft);
  padding-top: 10px;
}

.distribution-legend__item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto 46px;
  align-items: center;
  gap: 8px;
  color: var(--rf-text-muted);
  font-size: 12px;
  line-height: 1.4;
}

.distribution-legend__item span {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 7px;
  overflow: hidden;
  color: var(--rf-text);
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.distribution-legend__item i {
  flex: 0 0 auto;
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.distribution-legend__item strong {
  color: var(--rf-text);
  font-weight: 800;
}

.distribution-legend__item em {
  color: var(--rf-text-soft);
  font-style: normal;
  text-align: right;
}

.latest-warning-panel {
  display: flex;
  flex-direction: column;
  min-height: 522px;
  padding: 16px 18px;
}

.latest-warning-panel header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.latest-warning-list {
  display: grid;
  gap: 10px;
  overflow: auto;
  padding-right: 4px;
}

.latest-warning-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 8px 10px;
  width: 100%;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  padding: 10px 8px;
  text-align: left;
}

.latest-warning-item:hover,
.latest-warning-item--active {
  border-color: var(--rf-primary-line);
  background: var(--rf-primary-soft);
}

.latest-warning-item__title {
  overflow: hidden;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.latest-warning-item small {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.latest-warning-item em {
  grid-column: 2 / 4;
  color: var(--rf-text-muted);
  font-size: 12px;
  font-style: normal;
}

.warning-legend {
  display: grid;
  gap: 7px;
  min-width: 120px;
}

.warning-legend span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-legend i {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-critical {
  background: var(--rf-status-critical);
}

.legend-warning {
  background: var(--rf-status-warning);
}

.legend-watch {
  background: var(--rf-status-watch);
}

.legend-normal {
  background: var(--rf-status-normal);
}

.legend-empty {
  background: var(--rf-status-empty);
}

.ellipsis-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
  white-space: nowrap;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.table-actions .ant-btn {
  color: var(--rf-primary);
  border-color: var(--rf-primary-line);
  padding: 0 7px;
  font-size: 12px;
}

:deep(.warning-row--active > td) {
  background: var(--rf-primary-soft) !important;
}

@media (max-width: 1360px) {
  .warning-stat-grid,
  .risk-center {
    grid-template-columns: 1fr 1fr;
  }

  .risk-center > .map-panel {
    grid-column: 1 / -1;
    order: -1;
  }
}

@media (max-width: 920px) {
  .warning-stat-grid,
  .risk-center {
    grid-template-columns: 1fr;
  }

  .risk-center > .map-panel {
    order: 0;
  }

  .filter-field,
  .filter-field--range {
    min-width: 100%;
  }
}
</style>
