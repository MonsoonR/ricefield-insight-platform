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

    <div class="metric-dashboard">
      <ChartCard
        title="地块指标排行"
        :description="comparison ? `${comparison.metric_name}（${currentUnit}）` : '请选择指标后刷新。'"
        :loading="loading"
        :empty="rows.length === 0"
        :height="360"
      >
        <EChartView :option="rankOption" :height="360" />
      </ChartCard>

      <section class="panel region-compare">
        <h2 class="section-title">区域对比</h2>
        <div v-for="item in regionGroups" :key="item.region" class="region-compare__item">
          <strong>{{ item.region }}</strong>
          <span>平均值</span>
          <b>{{ item.average }} {{ currentUnit }}</b>
          <small>{{ item.count }} 个地块参与对比</small>
        </div>
      </section>

      <ChartCard title="状态分布" :loading="loading" :empty="statusDistribution.length === 0">
        <EChartView :option="statusOption" :height="360" />
      </ChartCard>
    </div>

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
const regionGroups = computed(() => {
  const grouped = new Map<string, { total: number; count: number }>();
  rows.value.forEach((item) => {
    const region = item.region || '未分区';
    const current = grouped.get(region) ?? { total: 0, count: 0 };
    current.total += Number(item.value) || 0;
    current.count += 1;
    grouped.set(region, current);
  });
  return [...grouped.entries()].map(([region, value]) => ({
    region,
    count: value.count,
    average: value.count ? Math.round((value.total / value.count) * 10) / 10 : 0,
  }));
});
const statusDistribution = computed(() => {
  const grouped = new Map<string, number>();
  rows.value.forEach((item) => {
    const status = item.quality_flag || 'normal';
    grouped.set(status, (grouped.get(status) ?? 0) + 1);
  });
  return [...grouped.entries()].map(([status, value]) => ({
    name: qualityLabel(status),
    value,
  }));
});

const rankOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 36, left: 48 },
  xAxis: { type: 'category', data: rows.value.map((item) => item.plot_code) },
  yAxis: { type: 'value', name: currentUnit.value, splitLine: { lineStyle: { color: '#edf2f0' } } },
  series: [{
    name: comparison.value?.metric_name ?? '指标值',
    type: 'bar',
    data: rows.value.map((item) => ({
      value: item.value,
      itemStyle: { color: qualityColor(item.quality_flag) },
    })),
    itemStyle: { borderRadius: [7, 7, 0, 0] },
  }],
}));
const statusOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item' },
  legend: { right: 8, top: 'middle', orient: 'vertical' },
  series: [{
    name: '质量状态',
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['34%', '50%'],
    data: statusDistribution.value,
    color: ['#16a36a', '#f6c343', '#f97316', '#ef3b2d', '#9ca3af'],
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

function qualityLabel(flag?: string | null) {
  const labels: Record<string, string> = {
    normal: '正常',
    missing: '关注',
    outlier: '预警',
    error: '严重',
  };
  return labels[flag || 'normal'] ?? (flag || '正常');
}

function qualityColor(flag?: string | null) {
  if (flag === 'missing') {
    return '#f6c343';
  }
  if (flag === 'outlier') {
    return '#f97316';
  }
  if (flag === 'error') {
    return '#ef3b2d';
  }
  return '#15905d';
}
</script>

<style scoped>
.metric-dashboard {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 300px minmax(300px, 0.7fr);
  gap: 16px;
}

.region-compare {
  display: grid;
  align-content: start;
  gap: 14px;
  padding: 18px 20px;
}

.region-compare__item {
  border: 1px solid var(--rf-border-soft);
  border-radius: 8px;
  background: linear-gradient(135deg, #f4faf7, #ffffff);
  padding: 16px;
}

.region-compare__item strong,
.region-compare__item span,
.region-compare__item b,
.region-compare__item small {
  display: block;
}

.region-compare__item strong {
  color: var(--rf-primary-dark);
  font-size: 17px;
}

.region-compare__item span,
.region-compare__item small {
  color: var(--rf-text-muted);
  font-size: 12px;
}

.region-compare__item b {
  margin: 8px 0 10px;
  color: var(--rf-text);
  font-size: 26px;
}

@media (max-width: 1280px) {
  .metric-dashboard {
    grid-template-columns: 1fr;
  }
}
</style>
