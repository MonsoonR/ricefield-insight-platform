<template>
  <PageContainer
    title="预警分析"
    description="汇总模拟场景中的缺失值、异常值和地块预警，辅助答辩展示数字孪生状态感知能力。"
  >
    <FilterBar>
      <MetricSelector v-model="filters.metricCode" :options="metricOptions" />
      <RegionSelector v-model="filters.region" />
      <a-select v-model:value="typeFilter" :options="typeOptions" placeholder="预警类型" />
      <a-button type="primary" :loading="loading" @click="loadWarnings">刷新预警</a-button>
    </FilterBar>

    <ErrorState v-if="error" :message="error" compact />

    <div class="page-grid page-grid--four">
      <StatCard
        v-for="card in summaryCards"
        :key="card.label"
        :label="card.label"
        :value="card.value"
        :note="card.note"
        :icon="card.label.includes('缺失') ? QuestionCircleOutlined : AlertOutlined"
        tone="orange"
      />
      <StatCard label="地图地块" :value="featureCollection.features.length" tone="green" :icon="EnvironmentOutlined" />
    </div>

    <div class="warning-layout">
      <CesiumMapPanel
        title="预警地块分布"
        :feature-collection="featureCollection"
        :height="460"
        :loading="loading"
        :selected-plot-id="selectedPlotId"
        @plot-click="handlePlotClick"
      >
        <template #legend>
          <div class="warning-legend">
            <strong>图例</strong>
            <span><i class="legend-high" />异常/错误</span>
            <span><i class="legend-mid" />缺失/临界</span>
            <span><i class="legend-good" />正常</span>
          </div>
        </template>
      </CesiumMapPanel>

      <section class="panel warning-detail">
        <h2 class="section-title">地块状态</h2>
        <EmptyState v-if="!selectedProperties" compact description="点击地图地块查看详情" />
        <template v-else>
          <div class="warning-detail__hero">
            <strong>{{ selectedProperties.plot_code || selectedProperties.plot_id }}</strong>
            <StatusTag :status="selectedProperties.quality_flag || selectedProperties.status" />
          </div>
          <dl>
            <div><dt>当前值</dt><dd><MetricValueTag :value="selectedProperties.value" :unit="selectedProperties.unit" :quality-flag="selectedProperties.quality_flag" /></dd></div>
            <div><dt>观测日期</dt><dd>{{ selectedProperties.observed_at || '--' }}</dd></div>
            <div><dt>所属区域</dt><dd>{{ selectedProperties.region || '--' }}</dd></div>
            <div><dt>数据来源</dt><dd>{{ selectedProperties.data_source_id || '--' }}</dd></div>
          </dl>
        </template>
      </section>
    </div>

    <div class="page-grid page-grid--two">
      <DataTable
        title="预警列表"
        :columns="columns"
        :data-source="filteredWarnings"
        :loading="loading"
        row-key="warning_id"
        :pagination="{ pageSize: 8 }"
        empty-text="当前筛选下暂无预警"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'warning_type'">
            <StatusTag :status="record.warning_type as string" />
          </template>
        </template>
      </DataTable>

      <ChartCard title="预警类型分布" :loading="loading" :empty="distributionData.length === 0">
        <EChartView :option="distributionOption" :height="280" />
      </ChartCard>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import {
  AlertOutlined,
  EnvironmentOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue';
import type { TableColumnsType } from 'ant-design-vue';
import type { EChartsOption } from 'echarts';
import { computed, onMounted, reactive, ref } from 'vue';

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
import { buildWarningSummary } from '@/services/twinAnalysis';
import type {
  MapFeatureCollection,
  MapFeatureProperties,
  Metric,
  RegionCode,
  WarningItem,
} from '@/types/api';

const loading = ref(false);
const error = ref('');
const metrics = ref<Metric[]>([]);
const warnings = ref<WarningItem[]>([]);
const featureCollection = ref<MapFeatureCollection>({ type: 'FeatureCollection', features: [] });
const selectedPlotId = ref('');
const selectedProperties = ref<MapFeatureProperties>();
const typeFilter = ref('all');
const filters = reactive<{ region: RegionCode; metricCode?: string }>({
  region: 'all',
  metricCode: undefined,
});

const typeOptions = [
  { label: '全部预警', value: 'all' },
  { label: '缺失值', value: 'missing' },
  { label: '异常值', value: 'outlier' },
  { label: '错误', value: 'error' },
];
const metricOptions = computed(() => metrics.value.map((item) => ({ label: item.metric_name, value: item.metric_code })));
const filteredWarnings = computed(() =>
  warnings.value.filter((item) => typeFilter.value === 'all' || item.warning_type === typeFilter.value),
);
const summaryCards = computed(() => buildWarningSummary(filteredWarnings.value));
const distributionData = computed(() => {
  const grouped = new Map<string, number>();
  filteredWarnings.value.forEach((item) => {
    grouped.set(item.warning_type, (grouped.get(item.warning_type) ?? 0) + 1);
  });
  return [...grouped.entries()].map(([name, value]) => ({ name: warningLabel(name), value }));
});
const distributionOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item' },
  legend: { right: 8, top: 'middle', orient: 'vertical' },
  series: [{
    type: 'pie',
    radius: ['48%', '72%'],
    center: ['36%', '50%'],
    data: distributionData.value,
    color: ['#f59e0b', '#ef4444', '#9ca3af'],
  }],
}));

const columns: TableColumnsType = [
  { title: '地块编号', dataIndex: 'plot_code', key: 'plot_code', width: 110 },
  { title: '区域', dataIndex: 'region', key: 'region', width: 110 },
  { title: '指标', dataIndex: 'metric_name', key: 'metric_name', width: 130 },
  { title: '类型', dataIndex: 'warning_type', key: 'warning_type', width: 110 },
  { title: '观测日期', dataIndex: 'observed_at', key: 'observed_at', width: 120 },
  { title: '说明', dataIndex: 'message', key: 'message' },
];

onMounted(async () => {
  await initialize();
});

async function initialize() {
  loading.value = true;
  try {
    const metricData = await fetchMetrics();
    metrics.value = metricData.items;
    filters.metricCode = metricData.items[0]?.metric_code;
    await loadWarnings();
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '预警分析基础数据加载失败。');
  } finally {
    loading.value = false;
  }
}

async function loadWarnings() {
  loading.value = true;
  error.value = '';
  try {
    const [warningData, layerData] = await Promise.all([
      fetchWarnings({ region: filters.region, metricCode: filters.metricCode }),
      fetchMapLayers({ region: filters.region, metricCode: filters.metricCode }),
    ]);
    warnings.value = warningData.items;
    featureCollection.value = layerData.layers[0]?.feature_collection ?? { type: 'FeatureCollection', features: [] };
  } catch (currentError) {
    error.value = getApiErrorMessage(currentError, '预警数据加载失败。');
  } finally {
    loading.value = false;
  }
}

function handlePlotClick(properties: MapFeatureProperties) {
  selectedPlotId.value = properties.plot_id ?? '';
  selectedProperties.value = properties;
}

function warningLabel(flag: string) {
  const labels: Record<string, string> = {
    missing: '缺失',
    outlier: '异常',
    error: '错误',
  };
  return labels[flag] ?? flag;
}
</script>

<style scoped>
.warning-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 14px;
}

.warning-detail {
  padding: 16px;
}

.warning-detail__hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
}

.warning-detail__hero strong {
  font-size: 28px;
  font-weight: 900;
}

.warning-detail dl {
  display: grid;
  gap: 12px;
  margin: 18px 0 0;
}

.warning-detail dt {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.warning-detail dd {
  margin: 4px 0 0;
  color: #1f2933;
  font-weight: 800;
}

.warning-legend {
  display: grid;
  gap: 7px;
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

.legend-high {
  background: #ef4444;
}

.legend-mid {
  background: #f59e0b;
}

.legend-good {
  background: #169b62;
}

@media (max-width: 1080px) {
  .warning-layout {
    grid-template-columns: 1fr;
  }
}
</style>
