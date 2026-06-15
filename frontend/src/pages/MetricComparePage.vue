<template>
  <PageContainer>
    <FilterBar>
      <div class="filter-field">
        <span>指标选择</span>
        <MetricSelector v-model="filters.metricCode" :options="metricOptions" :loading="loading" />
      </div>
      <div class="filter-field">
        <span>观测日期</span>
        <DateSelector v-model="filters.observedAt" :dates="dates" :loading="loading" />
      </div>
      <div class="filter-field">
        <span>区域</span>
        <RegionSelector v-model="filters.region" />
      </div>
      <div class="filter-actions">
        <a-button type="primary" :loading="loading" @click="loadComparison">
          <template #icon><SearchOutlined /></template>
          查询
        </a-button>
        <a-button :disabled="loading" @click="resetFilters">
          <template #icon><ReloadOutlined /></template>
          重置
        </a-button>
      </div>
      <div class="compare-summary">
        <InfoCircleOutlined />
        <span>{{ compareSummaryText }}</span>
      </div>
    </FilterBar>

    <a-alert v-if="stateMessage" :message="stateMessage" type="warning" show-icon />
    <ErrorState v-if="error" :message="error" compact />

    <div class="metric-stat-grid">
      <StatCard label="地块总数" :value="summary.total" note="参与对比地块" :icon="BarChartOutlined" />
      <StatCard label="指标均值" :value="summary.average" :note="`所有地块平均值${currentUnit ? ` / ${currentUnit}` : ''}`" tone="blue" :icon="CalculatorOutlined" />
      <StatCard label="最高值" :value="summary.maxValue" :note="summary.maxNote" tone="green" :icon="TrophyOutlined" />
      <StatCard label="最低值" :value="summary.minValue" :note="summary.minNote" tone="yellow" :icon="FallOutlined" />
      <StatCard label="异常地块数" :value="summary.abnormalCount" :note="summary.abnormalNote" tone="red" :icon="WarningOutlined" />
    </div>

    <div class="metric-dashboard">
      <ChartCard
        class="rank-card"
        :title="`地块排行（${metricTitle}）`"
        description="点击柱子或表格行可查看地块画像或定位到地图。"
        :loading="loading"
        :empty="rows.length === 0"
        :empty-text="emptyText"
        :height="360"
      >
        <EChartView :option="rankOption" :height="360" @click="handleRankClick" />
      </ChartCard>

      <section class="panel region-compare">
        <header>
          <h2 class="section-title">区域对比（{{ metricTitle }}）</h2>
          <p class="section-subtitle">按当前筛选结果前端聚合平均值、最高值、最低值和地块数量。</p>
        </header>
        <EmptyState v-if="regionGroups.length === 0" compact description="暂无区域对比数据" />
        <div v-else class="region-card-list">
          <article
            v-for="(item, index) in regionGroups"
            :key="item.region"
            class="region-card"
            :class="`region-card--${index % 2 === 0 ? 'primary' : 'blue'}`"
          >
            <div class="region-card__head">
              <strong>{{ item.region }}</strong>
              <span>{{ item.count }} 个地块</span>
            </div>
            <div class="region-card__value">
              <span>平均值</span>
              <b>{{ item.average }} <small>{{ currentUnit }}</small></b>
            </div>
            <dl>
              <div>
                <dt>最高值</dt>
                <dd>{{ item.maxValue }} {{ currentUnit }}<span>{{ item.maxPlot }}</span></dd>
              </div>
              <div>
                <dt>最低值</dt>
                <dd>{{ item.minValue }} {{ currentUnit }}<span>{{ item.minPlot }}</span></dd>
              </div>
            </dl>
          </article>
        </div>
      </section>

      <ChartCard
        title="状态分布"
        description="正常、关注、预警、严重地块数量和占比。"
        :loading="loading"
        :empty="rows.length === 0"
        :empty-text="emptyText"
        :height="360"
      >
        <EChartView :option="statusOption" :height="360" />
      </ChartCard>
    </div>

    <DataTable
      title="明细数据表"
      description="较均值差值 = 当前值 - 所有地块均值；较昨日变化基于最近两次观测数据计算。"
      :columns="columns"
      :data-source="rows"
      :loading="loading"
      row-key="plot_id"
      :pagination="{ pageSize: 10, showSizeChanger: false, showTotal: (total: number) => `共 ${total} 条数据` }"
      :scroll="{ x: 1040 }"
      :empty-text="emptyText"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'value'">
          <MetricValueTag
            :value="record.value as number | string | null"
            :unit="record.unit as string"
            :quality-flag="record.quality_flag as string"
          />
        </template>
        <template v-else-if="column.key === 'average_delta'">
          <span :class="deltaClass(record.average_delta as number | null)">
            {{ formatSigned(record.average_delta as number | null) }}
          </span>
        </template>
        <template v-else-if="column.key === 'previous_delta'">
          <span class="change-value" :class="deltaClass(record.previous_delta as number | null)">
            <RiseOutlined v-if="(record.previous_delta as number | null) !== null && Number(record.previous_delta) > 0" />
            <FallOutlined v-else-if="(record.previous_delta as number | null) !== null && Number(record.previous_delta) < 0" />
            {{ formatChange(record.previous_delta as number | null, record.previous_percent as number | null) }}
          </span>
        </template>
        <template v-else-if="column.key === 'quality_flag'">
          <StatusTag :status="record.quality_flag as string" />
        </template>
        <template v-else-if="column.key === 'data_source_id'">
          {{ sourceLabel(record.data_source_id as string | null | undefined) }}
        </template>
        <template v-else-if="column.key === 'actions'">
          <div class="table-actions">
            <a-button size="small" @click="goPlotDetail(record.plot_id as string)">查看画像</a-button>
            <a-button size="small" @click="goMapTwin(record.plot_id as string)">定位地图</a-button>
          </div>
        </template>
      </template>
    </DataTable>

    <section class="panel metric-note">
      <h2 class="section-title">指标说明</h2>
      <dl>
        <div>
          <dt>当前指标</dt>
          <dd>{{ currentMetric?.metric_name ?? '未找到指标' }}</dd>
        </div>
        <div>
          <dt>单位</dt>
          <dd>{{ currentMetric?.unit || '无' }}</dd>
        </div>
        <div>
          <dt>指标类别</dt>
          <dd>{{ currentMetric?.category || '未配置' }}</dd>
        </div>
        <div>
          <dt>正常范围</dt>
          <dd>{{ normalRangeText }}</dd>
        </div>
      </dl>
      <p>{{ currentMetric?.description || '指标字典暂未配置说明。' }}</p>
    </section>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  BarChartOutlined,
  CalculatorOutlined,
  FallOutlined,
  InfoCircleOutlined,
  ReloadOutlined,
  RiseOutlined,
  SearchOutlined,
  TrophyOutlined,
  WarningOutlined,
} from '@ant-design/icons-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  fetchDates,
  fetchMetricCompare,
  fetchMetrics,
  fetchPlotSeries,
  getApiErrorMessage,
} from '@/api';
import {
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
  StatCard,
  StatusTag,
} from '@/components/base';
import { buildMapTwinLocation, buildPlotDetailRequestPlan } from '@/services/pageLinkage';
import { sortMetricCompareRows } from '@/services/twinAnalysis';
import type { Metric, MetricCompareItem, MetricCompareResponse, PlotSeriesResponse, RegionCode } from '@/types/api';
import type { TableColumnsType } from '@/types/table';
import type { StatusLevel } from '@/utils/status';
import { mapQualityToStatus, statusLevelMeta } from '@/utils/status';

interface RowSupplement {
  previousDelta: number | null;
  previousPercent: number | null;
  batchId?: string | null;
  dataSourceId?: string | null;
}

type CompareRow = MetricCompareItem & {
  average_delta: number | null;
  previous_delta: number | null;
  previous_percent: number | null;
  batch_id?: string | null;
  data_source_id?: string | null;
  status_level: StatusLevel;
};

const STATUS_ORDER: StatusLevel[] = ['normal', 'watch', 'warning', 'critical'];
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
const dates = ref<string[]>([]);
const comparison = ref<MetricCompareResponse>();
const supplements = ref<Record<string, RowSupplement>>({});
const filters = reactive<{ region: RegionCode; metricCode?: string; observedAt?: string }>({
  region: 'all',
  metricCode: undefined,
  observedAt: undefined,
});

const metricOptions = computed(() =>
  metrics.value.map((item) => ({
    label: `${item.metric_name}${item.unit ? `（${item.unit}）` : ''}`,
    value: item.metric_code,
    unit: item.unit,
  })),
);
const currentMetric = computed(() =>
  metrics.value.find((item) => item.metric_code === filters.metricCode),
);
const baseRows = computed(() => sortMetricCompareRows(comparison.value?.items ?? []));
const numericValues = computed(() =>
  baseRows.value
    .map((item) => toNumber(item.value))
    .filter((value): value is number => value !== null),
);
const averageValue = computed(() => {
  if (numericValues.value.length === 0) {
    return null;
  }
  const total = numericValues.value.reduce((sum, value) => sum + value, 0);
  return total / numericValues.value.length;
});
const rows = computed<CompareRow[]>(() =>
  baseRows.value.map((item) => {
    const value = toNumber(item.value);
    const supplement = supplements.value[item.plot_id];
    return {
      ...item,
      average_delta: value !== null && averageValue.value !== null
        ? round(value - averageValue.value)
        : null,
      previous_delta: supplement?.previousDelta ?? null,
      previous_percent: supplement?.previousPercent ?? null,
      batch_id: supplement?.batchId,
      data_source_id: supplement?.dataSourceId,
      status_level: mapQualityToStatus(item.quality_flag),
    };
  }),
);
const currentUnit = computed(() => comparison.value?.items[0]?.unit ?? currentMetric.value?.unit ?? '');
const metricTitle = computed(() => {
  if (!currentMetric.value && filters.metricCode) {
    return filters.metricCode;
  }
  const name = currentMetric.value?.metric_name ?? comparison.value?.metric_name ?? '当前指标';
  return currentUnit.value ? `${name} ${currentUnit.value}` : name;
});
const selectedRegionText = computed(() => {
  if (filters.region === 'east') {
    return '试验一区';
  }
  if (filters.region === 'west') {
    return '试验二区';
  }
  return '全部区域';
});
const compareSummaryText = computed(() =>
  `共 ${rows.value.length} 个地块参与对比（${selectedRegionText.value}）`,
);
const emptyText = computed(() => {
  if (filters.metricCode && !currentMetric.value) {
    return '未找到指标';
  }
  if (filters.observedAt && dates.value.length > 0 && !dates.value.includes(filters.observedAt)) {
    return '当前日期暂无观测数据';
  }
  return '当前筛选下暂无对比数据';
});
const stateMessage = computed(() => {
  if (filters.metricCode && !currentMetric.value) {
    return '未找到指标';
  }
  if (!loading.value && filters.observedAt && rows.value.length === 0) {
    return '当前日期暂无观测数据';
  }
  return '';
});
const normalRangeText = computed(() => {
  const range = currentMetric.value?.normal_range;
  if (!range || (range.min === undefined && range.max === undefined)) {
    return '未配置';
  }
  const min = range.min ?? '-∞';
  const max = range.max ?? '+∞';
  return `${min} - ${max}${currentUnit.value ? ` ${currentUnit.value}` : ''}`;
});
const summary = computed(() => {
  const normalRows = rows.value.filter((item) => item.status_level === 'normal').length;
  const abnormalCount = Math.max(rows.value.length - normalRows, 0);
  const abnormalPercent = rows.value.length ? round((abnormalCount / rows.value.length) * 100, 1) : 0;
  const sortedByValue = [...rows.value]
    .filter((item) => toNumber(item.value) !== null)
    .sort((a, b) => Number(b.value) - Number(a.value));
  const max = sortedByValue[0];
  const min = sortedByValue[sortedByValue.length - 1];
  return {
    total: rows.value.length,
    average: averageValue.value === null ? '--' : formatNumber(averageValue.value),
    maxValue: max ? formatNumber(max.value) : '--',
    minValue: min ? formatNumber(min.value) : '--',
    maxNote: max ? `${max.plot_code} · ${max.region || '未分区'}` : '暂无数据',
    minNote: min ? `${min.plot_code} · ${min.region || '未分区'}` : '暂无数据',
    abnormalCount,
    abnormalNote: `占比 ${abnormalPercent}%`,
  };
});
const regionGroups = computed(() => {
  const grouped = new Map<string, CompareRow[]>();
  rows.value.forEach((item) => {
    const region = item.region || '未分区';
    grouped.set(region, [...(grouped.get(region) ?? []), item]);
  });
  return [...grouped.entries()].sort(([left], [right]) => regionOrder(left) - regionOrder(right)).map(([region, items]) => {
    const values = items
      .map((item) => toNumber(item.value))
      .filter((value): value is number => value !== null);
    const sorted = [...items]
      .filter((item) => toNumber(item.value) !== null)
      .sort((a, b) => Number(b.value) - Number(a.value));
    return {
      region,
      count: items.length,
      average: values.length
        ? formatNumber(values.reduce((sum, value) => sum + value, 0) / values.length)
        : '--',
      maxValue: sorted[0] ? formatNumber(sorted[0].value) : '--',
      minValue: sorted[sorted.length - 1] ? formatNumber(sorted[sorted.length - 1].value) : '--',
      maxPlot: sorted[0]?.plot_code ?? '无',
      minPlot: sorted[sorted.length - 1]?.plot_code ?? '无',
    };
  });
});
const statusDistribution = computed(() =>
  STATUS_ORDER.map((level) => {
    const count = rows.value.filter((item) => item.status_level === level).length;
    const percent = rows.value.length ? round((count / rows.value.length) * 100, 1) : 0;
    return {
      level,
      name: statusLevelMeta[level].label,
      value: count,
      percent,
      itemStyle: { color: STATUS_COLORS[level] },
    };
  }),
);

const rankOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: (params: unknown) => {
      const first = Array.isArray(params) ? params[0] : undefined;
      const data = first && typeof first === 'object' && 'data' in first
        ? (first as { data?: { plotName?: string; region?: string; value?: number | string } }).data
        : undefined;
      return data
        ? `${data.plotName}<br/>${data.region}<br/>${comparison.value?.metric_name ?? '指标值'}：${data.value} ${currentUnit.value}`
        : '';
    },
  },
  legend: {
    top: 0,
    data: STATUS_ORDER.map((level) => statusLevelMeta[level].label),
    textStyle: { color: '#6B7280', fontSize: 12 },
  },
  grid: { top: 44, right: 22, bottom: 42, left: 48 },
  xAxis: {
    type: 'category',
    data: rows.value.map((item) => item.plot_code),
    axisLine: { show: false },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    name: currentUnit.value,
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#EDF2EF' } },
  },
  series: [
    ...STATUS_ORDER.map((level) => ({
      name: statusLevelMeta[level].label,
      type: 'bar' as const,
      itemStyle: { color: STATUS_COLORS[level] },
      data: rows.value.map((item) => (item.status_level === level
        ? {
            value: item.value,
            plotId: item.plot_id,
            plotName: item.plot_name || item.plot_code,
            region: item.region,
            itemStyle: { color: STATUS_COLORS[level], borderRadius: [5, 5, 0, 0] },
          }
        : null)),
      barWidth: 30,
      stack: 'rank',
    })),
    {
      name: '均值参考线',
      type: 'line',
      data: rows.value.map(() => averageValue.value),
      symbol: 'none',
      lineStyle: { color: '#6B7280', width: 1, type: 'dashed' },
      markLine: averageValue.value === null ? undefined : {
        symbol: 'none',
        label: {
          formatter: `均值 ${formatNumber(averageValue.value)}`,
          color: '#1F2937',
        },
        lineStyle: { color: '#6B7280', type: 'dashed' },
        data: [{ yAxis: averageValue.value }],
      },
    },
  ],
}));
const statusOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'item',
    formatter: (params: unknown) => {
      const item = params as { name?: string; value?: number; data?: { percent?: number } };
      return `${item.name}：${item.value ?? 0} 个（${item.data?.percent ?? 0}%）`;
    },
  },
  title: {
    text: String(rows.value.length),
    subtext: '总地块',
    left: '32%',
    top: '43%',
    textAlign: 'center',
    textStyle: { color: '#1F2937', fontSize: 28, fontWeight: 800 },
    subtextStyle: { color: '#6B7280', fontSize: 12 },
  },
  legend: {
    right: 0,
    top: 'middle',
    orient: 'vertical',
    itemWidth: 10,
    itemHeight: 10,
    formatter: (name: string) => {
      const item = statusDistribution.value.find((entry) => entry.name === name);
      return item ? `${name}  ${item.value} (${item.percent}%)` : name;
    },
  },
  series: [{
    name: '状态分布',
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['32%', '50%'],
    avoidLabelOverlap: true,
    label: { show: false },
    data: statusDistribution.value,
  }],
}));

const columns: TableColumnsType = [
  { title: '排名', dataIndex: 'rank', key: 'rank', width: 54 },
  { title: '地块编号', dataIndex: 'plot_code', key: 'plot_code', width: 86 },
  { title: '地块名称', dataIndex: 'plot_name', key: 'plot_name', width: 110 },
  { title: '区域', dataIndex: 'region', key: 'region', width: 88 },
  { title: '当前指标值', dataIndex: 'value', key: 'value', width: 110 },
  { title: '较均值差值', dataIndex: 'average_delta', key: 'average_delta', width: 98 },
  { title: '较昨日变化', dataIndex: 'previous_delta', key: 'previous_delta', width: 112 },
  { title: '状态', dataIndex: 'quality_flag', key: 'quality_flag', width: 76 },
  { title: '数据来源', dataIndex: 'data_source_id', key: 'data_source_id', width: 88 },
  { title: '观测批次', dataIndex: 'batch_id', key: 'batch_id', width: 120, ellipsis: true },
  { title: '操作', key: 'actions', width: 146 },
];

onMounted(async () => {
  await initialize();
});

async function initialize() {
  loading.value = true;
  try {
    const [metricData, dateData] = await Promise.all([fetchMetrics(), fetchDates()]);
    metrics.value = metricData.items;
    dates.value = dateData.items;
    filters.metricCode =
      metricData.items.find((item) => item.metric_code === 'chlorophyll')?.metric_code
      ?? metricData.items[0]?.metric_code;
    filters.observedAt = dateData.items[dateData.items.length - 1];
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '指标对比基础数据加载失败。');
  } finally {
    loading.value = false;
  }
  await loadComparison();
}

async function loadComparison() {
  if (!filters.metricCode || !currentMetric.value) {
    comparison.value = undefined;
    supplements.value = {};
    error.value = '';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const data = await fetchMetricCompare({
      region: filters.region,
      metricCode: filters.metricCode,
      observedAt: filters.observedAt,
    });
    comparison.value = data;
    supplements.value = await loadSupplements(data.items);
  } catch (currentError) {
    comparison.value = undefined;
    supplements.value = {};
    error.value = getApiErrorMessage(currentError, 'API 请求失败，请稍后重试。');
  } finally {
    loading.value = false;
  }
}

async function loadSupplements(items: MetricCompareItem[]) {
  if (!filters.metricCode || items.length === 0) {
    return {};
  }
  const settled = await Promise.allSettled(
    items.map((item) =>
      fetchPlotSeries({
        plotId: item.plot_id,
        metricCode: filters.metricCode,
      }).then((series) => [item.plot_id, buildSupplement(series, item.observed_at)] as const),
    ),
  );
  const next: Record<string, RowSupplement> = {};
  settled.forEach((result) => {
    if (result.status === 'fulfilled') {
      const [plotId, supplement] = result.value;
      next[plotId] = supplement;
    }
  });
  return next;
}

function buildSupplement(series: PlotSeriesResponse, observedAt: string): RowSupplement {
  const currentSeries = series.series.find((item) => item.metric_code === filters.metricCode);
  const points = [...(currentSeries?.points ?? [])].sort((a, b) =>
    a.observed_at.localeCompare(b.observed_at),
  );
  const currentIndex = points.findIndex((point) => point.observed_at === observedAt);
  const currentPoint = currentIndex >= 0 ? points[currentIndex] : points[points.length - 1];
  const previousPoint = currentIndex > 0 ? points[currentIndex - 1] : undefined;
  const currentValue = toNumber(currentPoint?.value);
  const previousValue = toNumber(previousPoint?.value);
  if (currentValue === null || previousValue === null || previousValue === 0) {
    return {
      previousDelta: null,
      previousPercent: null,
      batchId: currentPoint?.batch_id,
      dataSourceId: currentPoint?.data_source_id,
    };
  }
  const delta = round(currentValue - previousValue);
  return {
    previousDelta: delta,
    previousPercent: round((delta / Math.abs(previousValue)) * 100, 1),
    batchId: currentPoint?.batch_id,
    dataSourceId: currentPoint?.data_source_id,
  };
}

function resetFilters() {
  filters.region = 'all';
  filters.metricCode =
    metrics.value.find((item) => item.metric_code === 'chlorophyll')?.metric_code
    ?? metrics.value[0]?.metric_code;
  filters.observedAt = dates.value[dates.value.length - 1];
  void loadComparison();
}

function handleRankClick(params: unknown) {
  const data = params && typeof params === 'object' && 'data' in params
    ? (params as { data?: { plotId?: string } }).data
    : undefined;
  if (data?.plotId) {
    goPlotDetail(data.plotId);
  }
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

function toNumber(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === '') {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatNumber(value: number | string | null | undefined, precision = 1) {
  const parsed = toNumber(value);
  if (parsed === null) {
    return '--';
  }
  return String(round(parsed, precision));
}

function formatSigned(value: number | null) {
  if (value === null) {
    return '--';
  }
  if (value > 0) {
    return `+${formatNumber(value)}`;
  }
  return formatNumber(value);
}

function formatChange(delta: number | null, percent: number | null) {
  if (delta === null) {
    return '--';
  }
  const percentText = percent === null ? '' : `（${formatSigned(percent)}%）`;
  return `${formatSigned(delta)}${percentText}`;
}

function round(value: number, precision = 1) {
  const factor = 10 ** precision;
  return Math.round(value * factor) / factor;
}

function deltaClass(value: number | null) {
  if (value === null || value === 0) {
    return 'delta-neutral';
  }
  return value > 0 ? 'delta-up' : 'delta-down';
}

function sourceLabel(value?: string | null) {
  if (!value) {
    return '--';
  }
  if (value.includes('simulated')) {
    return '模拟数据';
  }
  return value;
}

function regionOrder(region: string) {
  if (region === '试验一区') {
    return 1;
  }
  if (region === '试验二区') {
    return 2;
  }
  return 99;
}
</script>

<style scoped>
.filter-field {
  display: grid;
  gap: 6px;
  min-width: 220px;
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
  min-width: 88px;
}

.compare-summary {
  display: flex;
  flex-basis: 100%;
  align-items: center;
  gap: 8px;
  color: var(--rf-primary);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.4;
}

.metric-stat-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.metric-dashboard {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(300px, 0.74fr) minmax(300px, 0.74fr);
  gap: 16px;
}

.region-compare {
  display: grid;
  align-content: start;
  gap: 16px;
  padding: 16px 18px 18px;
}

.region-card-list {
  display: grid;
  gap: 14px;
}

.region-card {
  display: grid;
  gap: 14px;
  min-height: 174px;
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  padding: 16px;
}

.region-card--primary {
  background: linear-gradient(135deg, var(--rf-primary-soft), var(--rf-surface));
}

.region-card--blue {
  background: linear-gradient(135deg, #eef5ff, var(--rf-surface));
}

.region-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.region-card__head strong {
  color: var(--rf-primary-dark);
  font-size: 17px;
}

.region-card__head span,
.region-card__value span,
.region-card dt {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.region-card__value b {
  display: block;
  margin-top: 4px;
  color: var(--rf-text);
  font-size: 26px;
  line-height: 1.15;
}

.region-card__value small {
  font-size: 12px;
  font-weight: 600;
}

.region-card dl,
.metric-note dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

.region-card dl {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.region-card dd,
.metric-note dd {
  margin: 0;
  color: var(--rf-text);
  font-size: 13px;
  font-weight: 700;
}

.region-card dd span {
  display: block;
  margin-top: 2px;
  color: var(--rf-text-soft);
  font-size: 12px;
  font-weight: 500;
}

.change-value {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.delta-up {
  color: var(--rf-status-normal);
}

.delta-down {
  color: var(--rf-status-critical);
}

.delta-neutral {
  color: var(--rf-text-muted);
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

.metric-note {
  padding: 18px 20px;
}

.metric-note dl {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 14px;
}

.metric-note dt {
  margin-bottom: 4px;
  color: var(--rf-text-muted);
  font-size: 12px;
}

.metric-note p {
  margin: 14px 0 0;
  color: var(--rf-text-muted);
  font-size: 13px;
  line-height: 1.7;
}

@media (max-width: 1360px) {
  .metric-stat-grid,
  .metric-dashboard {
    grid-template-columns: 1fr 1fr;
  }

  .rank-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 920px) {
  .metric-stat-grid,
  .metric-dashboard,
  .metric-note dl {
    grid-template-columns: 1fr;
  }

  .filter-field {
    min-width: 100%;
  }

  .filter-actions {
    align-self: auto;
  }
}
</style>
