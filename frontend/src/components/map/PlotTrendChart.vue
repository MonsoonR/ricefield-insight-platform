<template>
  <div class="plot-trend-chart">
    <a-skeleton v-if="loading" active :paragraph="{ rows: 6 }" />

    <ErrorState
      v-else-if="error"
      title="趋势加载失败"
      :message="error"
    />

    <EmptyState
      v-else-if="!hasTrendData"
      description="当前地块在所选指标下暂无趋势数据"
    />

    <div v-else class="plot-trend-chart__content">
      <div class="plot-trend-chart__meta">
        <strong>{{ series?.metric_name ?? '指标趋势' }}</strong>
        <small>{{ series?.unit ? `单位：${series.unit}` : '未配置单位' }}</small>
      </div>
      <div ref="chartElement" class="plot-trend-chart__canvas" :style="{ height: `${height}px` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';

import { EmptyState, ErrorState } from '@/components/base';
import { initChart, type EChartsOption } from '@/utils/echarts';
import type { PlotMetricSeries, PlotSeriesPoint } from '@/types/mapAnalysis';

const props = withDefaults(
  defineProps<{
    series?: PlotMetricSeries;
    loading?: boolean;
    error?: string;
    height?: number;
  }>(),
  {
    loading: false,
    error: '',
    height: 260,
  },
);

const chartElement = ref<HTMLElement>();
let chart: ReturnType<typeof initChart> | undefined;
let resizeObserver: ResizeObserver | undefined;

const chartPoints = computed(() => props.series?.points ?? []);
const chartValues = computed(() => chartPoints.value.map((point) => toChartValue(point.value)));
const hasTrendData = computed(() => chartValues.value.some((value) => value !== null));

watch(
  () => [props.series, props.loading, props.error] as const,
  () => {
    void renderChart();
  },
  { deep: true, immediate: true },
);

onBeforeUnmount(() => {
  disposeChart();
});

async function renderChart() {
  await nextTick();

  if (props.loading || props.error || !hasTrendData.value || !chartElement.value) {
    disposeChart();
    return;
  }

  if (!chart) {
    chart = initChart(chartElement.value);
    resizeObserver = new ResizeObserver(() => {
      chart?.resize();
    });
    resizeObserver.observe(chartElement.value);
  }

  chart.setOption(buildChartOption(), true);
  chart.resize();
}

function buildChartOption(): EChartsOption {
  return {
    color: ['#2f7d4f'],
    grid: {
      top: 24,
      right: 18,
      bottom: 42,
      left: 52,
    },
    tooltip: {
      trigger: 'axis',
      confine: true,
      formatter(params) {
        const item = Array.isArray(params) ? params[0] : params;
        const point = chartPoints.value[item.dataIndex] as PlotSeriesPoint | undefined;
        if (!point) {
          return '';
        }

        return [
          `<strong>${escapeHtml(props.series?.metric_name ?? '指标')}</strong>`,
          `日期：${escapeHtml(point.observed_at)}`,
          `值：${escapeHtml(formatValue(point.value, props.series?.unit))}`,
          `质量标记：${escapeHtml(point.quality_flag ?? '-')}`,
          `观测批次：${escapeHtml(point.batch_id ?? '-')}`,
          `数据来源：${escapeHtml(point.data_source_id ?? '-')}`,
        ].join('<br/>');
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartPoints.value.map((point) => point.observed_at),
      axisLabel: {
        color: '#667085',
      },
      axisLine: {
        lineStyle: {
          color: '#d7e2dc',
        },
      },
    },
    yAxis: {
      type: 'value',
      name: props.series?.unit ? `值 (${props.series.unit})` : '值',
      nameTextStyle: {
        color: '#667085',
      },
      axisLabel: {
        color: '#667085',
      },
      splitLine: {
        lineStyle: {
          color: '#edf3ef',
        },
      },
    },
    series: [
      {
        name: props.series?.metric_name ?? '指标趋势',
        type: 'line',
        smooth: true,
        connectNulls: false,
        symbolSize: 7,
        data: chartValues.value,
        lineStyle: {
          width: 2.5,
        },
        areaStyle: {
          opacity: 0.08,
        },
      },
    ],
  };
}

function disposeChart() {
  resizeObserver?.disconnect();
  resizeObserver = undefined;
  chart?.dispose();
  chart = undefined;
}

function toChartValue(value: PlotSeriesPoint['value']) {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue : null;
}

function formatValue(value: PlotSeriesPoint['value'], unit?: string) {
  if (value === null || value === undefined || value === '') {
    return unit ? `无数据 ${unit}` : '无数据';
  }

  return unit ? `${value} ${unit}` : String(value);
}

function escapeHtml(value: string | number) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
</script>

<style scoped>
.plot-trend-chart {
  min-width: 0;
}

.plot-trend-chart__content {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.plot-trend-chart__meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  color: #1f2933;
}

.plot-trend-chart__meta strong {
  font-size: 15px;
}

.plot-trend-chart__meta small {
  color: #667085;
  font-size: 12px;
}

.plot-trend-chart__canvas {
  min-height: 220px;
  min-width: 0;
}
</style>
