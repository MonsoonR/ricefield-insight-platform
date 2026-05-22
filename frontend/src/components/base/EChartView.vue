<template>
  <div ref="chartRef" class="echart-view" :style="{ height: `${height}px` }" />
</template>

<script setup lang="ts">
import type { ECharts, EChartsOption } from 'echarts';
import { init } from 'echarts';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';

const emit = defineEmits<{
  click: [params: unknown];
}>();

const props = withDefaults(
  defineProps<{
    option: EChartsOption;
    height?: number;
  }>(),
  {
    height: 280,
  },
);

const chartRef = ref<HTMLDivElement>();
let chart: ECharts | undefined;
let resizeObserver: ResizeObserver | undefined;

function handleChartClick(params: unknown) {
  emit('click', params);
}

onMounted(() => {
  if (!chartRef.value) {
    return;
  }
  chart = init(chartRef.value);
  chart.on('click', handleChartClick);
  chart.setOption(props.option, true);
  resizeObserver = new ResizeObserver(() => chart?.resize());
  resizeObserver.observe(chartRef.value);
});

watch(
  () => props.option,
  (option) => {
    chart?.setOption(option, true);
  },
  { deep: true },
);

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  chart?.off('click', handleChartClick);
  chart?.dispose();
  chart = undefined;
});
</script>

<style scoped>
.echart-view {
  width: 100%;
  min-width: 0;
}
</style>
