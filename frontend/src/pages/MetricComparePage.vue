<template>
  <PageContainer
    title="指标对比"
    description="按指标、日期和区域比较不同地块的最新观测值，用于展示数字孪生场景中的空间差异。"
  >
    <FilterBar>
      <MetricSelector v-model="filters.metricCode" :options="metricOptions" :loading="loading" />
      <DateSelector v-model="filters.observedAt" :dates="dates" :loading="loading" />
      <RegionSelector v-model="filters.region" />
      <a-button type="primary" :loading="loading" @click="loadComparison">刷新对比</a-button>
    </FilterBar>

    <ErrorState v-if="error" :message="error" compact />

    <div class="page-grid page-grid--four">
      <StatCard label="参与地块" :value="comparison?.total ?? 0" :icon="BorderOutlined" />
      <StatCard label="当前指标" :value="comparison?.metric_name || '--'" tone="green" :icon="LineChartOutlined" />
      <StatCard label="观测日期" :value="comparison?.observed_at || '--'" tone="cyan" :icon="CalendarOutlined" />
      <StatCard label="预警地块" :value="warningCount" tone="orange" :icon="AlertOutlined" />
    </div>

    <ChartCard
      title="地块指标排行"
      :description="comparison ? `${comparison.metric_name}（${currentUnit}）` : '请选择指标后刷新。'"
      :loading="loading"
      :empty="rows.length === 0"
      :height="360"
    >
      <EChartView :option="rankOption" :height="360" />
    </ChartCard>

    <DataTable
      title="指标对比明细"
      :columns="columns"
      :data-source="rows"
      :loading="loading"
      row-key="plot_id"
      :pagination="{ pageSize: 10 }"
      empty-text="当前筛选下暂无对比数据"
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
import {
  AlertOutlined,
  BorderOutlined,
  CalendarOutlined,
  LineChartOutlined,
} from '@ant-design/icons-vue';
import type { TableColumnsType } from 'ant-design-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref, watch } from 'vue';

import {
  fetchDates,
  fetchMetricCompare,
  fetchMetrics,
  getApiErrorMessage,
} from '@/api';
import {
  ChartCard,
  DataTable,
  DateSelector,
  EChartView,
  ErrorState,
  FilterBar,
  MetricSelector,
  MetricValueTag,
  PageContainer,
  RegionSelector,
  StatCard,
  StatusTag,
} from '@/components/base';
import { sortMetricCompareRows } from '@/services/twinAnalysis';
import type { Metric, MetricCompareResponse, RegionCode } from '@/types/api';

const loading = ref(false);
const error = ref('');
const metrics = ref<Metric[]>([]);
const dates = ref<string[]>([]);
const comparison = ref<MetricCompareResponse>();
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
const rows = computed(() => sortMetricCompareRows(comparison.value?.items ?? []));
const currentUnit = computed(() => rows.value[0]?.unit ?? '');
const warningCount = computed(() =>
  rows.value.filter((item) => item.quality_flag && item.quality_flag !== 'normal').length,
);

const rankOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 36, left: 48 },
  xAxis: { type: 'category', data: rows.value.map((item) => item.plot_code) },
  yAxis: { type: 'value', name: currentUnit.value, splitLine: { lineStyle: { color: '#edf2f0' } } },
  series: [{
    name: comparison.value?.metric_name ?? '指标值',
    type: 'bar',
    data: rows.value.map((item) => item.value),
    itemStyle: { color: '#07883f' },
  }],
}));

const columns: TableColumnsType = [
  { title: '排名', dataIndex: 'rank', key: 'rank', width: 80 },
  { title: '地块编号', dataIndex: 'plot_code', key: 'plot_code', width: 120 },
  { title: '区域', dataIndex: 'region', key: 'region', width: 110 },
  { title: '指标值', dataIndex: 'value', key: 'value', width: 140 },
  { title: '观测日期', dataIndex: 'observed_at', key: 'observed_at', width: 130 },
  { title: '质量状态', dataIndex: 'quality_flag', key: 'quality_flag', width: 120 },
];

onMounted(async () => {
  await initialize();
});

watch(() => [filters.region, filters.metricCode, filters.observedAt], () => {
  void loadComparison();
});

async function initialize() {
  loading.value = true;
  try {
    const [metricData, dateData] = await Promise.all([fetchMetrics(), fetchDates()]);
    metrics.value = metricData.items;
    dates.value = dateData.items;
    filters.metricCode = metricData.items[0]?.metric_code;
    filters.observedAt = dateData.items[dateData.items.length - 1];
    await loadComparison();
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '指标对比基础数据加载失败。');
  } finally {
    loading.value = false;
  }
}

async function loadComparison() {
  if (!filters.metricCode) {
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    comparison.value = await fetchMetricCompare({
      region: filters.region,
      metricCode: filters.metricCode,
      observedAt: filters.observedAt,
    });
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '指标对比数据加载失败。');
  } finally {
    loading.value = false;
  }
}
</script>
