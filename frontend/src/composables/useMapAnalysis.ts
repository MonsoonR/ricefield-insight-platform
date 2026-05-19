import type { Dayjs } from 'dayjs';
import { computed, ref, watch } from 'vue';

import {
  fetchMapLayers,
  fetchMetricOptions,
  fetchObservationDates,
  fetchPlotSeries,
} from '@/api/mapAnalysis';
import {
  getMapApiErrorMessage,
  latestPointForSelection,
  trendSeriesForMetric,
  type MapFeatureCollection,
  type MapFeatureProperties,
  type MapLayersResponse,
} from '@/services/mapAnalysis';
import type { MetricOption, RegionCode } from '@/types/common';
import type { PlotMetricSeries, PlotSeriesPoint } from '@/types/mapAnalysis';

const EMPTY_COLLECTION: MapFeatureCollection = {
  type: 'FeatureCollection',
  features: [],
};

export function useMapAnalysis() {
  const region = ref<RegionCode>('all');
  const metricCode = ref('crop_growth');
  const observedDate = ref<Dayjs>();

  const metricOptions = ref<MetricOption[]>([]);
  const availableDates = ref<string[]>([]);
  const mapLayers = ref<MapLayersResponse>();
  const selectedPlot = ref<MapFeatureProperties>();
  const selectedObservation = ref<PlotSeriesPoint>();
  const plotTrend = ref<PlotMetricSeries>();

  const loading = ref(false);
  const detailLoading = ref(false);
  const trendLoading = ref(false);
  const error = ref('');
  const trendError = ref('');

  let layerRequestId = 0;
  let detailRequestId = 0;
  let suppressObservedDateReload = false;

  const observedAt = computed(() => observedDate.value?.format('YYYY-MM-DD'));
  const featureCollection = computed(
    () => mapLayers.value?.layers?.[0]?.feature_collection ?? EMPTY_COLLECTION,
  );
  const selectedPlotId = computed(() => selectedPlot.value?.plot_id);
  const selectedMetricOption = computed(
    () => metricOptions.value.find((item) => item.value === metricCode.value),
  );

  async function loadInitialData() {
    loading.value = true;
    error.value = '';

    try {
      metricOptions.value = await fetchMetricOptions();
      if (!metricOptions.value.some((item) => item.value === metricCode.value)) {
        metricCode.value = metricOptions.value[0]?.value ?? metricCode.value;
      }
      await Promise.all([loadDates(), loadLayers()]);
    } catch (currentError) {
      error.value = getMapApiErrorMessage(currentError, '地图分析数据加载失败，请检查后端接口和模拟场景服务状态。');
    } finally {
      loading.value = false;
    }
  }

  async function loadDates() {
    if (!metricCode.value) {
      availableDates.value = [];
      return;
    }

    availableDates.value = await fetchObservationDates(metricCode.value);
  }

  async function loadLayers() {
    const requestId = ++layerRequestId;
    loading.value = true;
    error.value = '';

    try {
      const response = await fetchMapLayers({
        region: region.value,
        metricCode: metricCode.value,
        observedAt: observedAt.value,
      });
      if (requestId !== layerRequestId) {
        return;
      }

      mapLayers.value = response;
      if (
        selectedPlot.value?.plot_id
        && response.layers?.[0]?.feature_collection.features
      ) {
        const updatedFeature = response.layers[0].feature_collection.features.find(
          (feature) => feature.properties.plot_id === selectedPlot.value?.plot_id,
        );
        if (updatedFeature) {
          selectedPlot.value = updatedFeature.properties;
        } else {
          selectedPlot.value = undefined;
          selectedObservation.value = undefined;
          plotTrend.value = undefined;
        }
      }
    } catch (currentError) {
      if (requestId === layerRequestId) {
        error.value = getMapApiErrorMessage(currentError, '地图图层加载失败，请稍后重试或检查筛选条件。');
      }
    } finally {
      if (requestId === layerRequestId) {
        loading.value = false;
      }
    }
  }

  async function selectPlot(properties: MapFeatureProperties) {
    selectedPlot.value = properties;
    selectedObservation.value = undefined;
    plotTrend.value = undefined;
    trendError.value = '';

    await loadSelectedPlotSeries();
  }

  async function loadSelectedPlotSeries() {
    if (!selectedPlot.value?.plot_id || !metricCode.value) {
      return;
    }

    const requestId = ++detailRequestId;
    detailLoading.value = true;
    trendLoading.value = true;
    trendError.value = '';

    try {
      const response = await fetchPlotSeries({
        plotId: selectedPlot.value.plot_id,
        metricCode: metricCode.value,
      });
      if (requestId !== detailRequestId) {
        return;
      }

      plotTrend.value = trendSeriesForMetric(response, metricCode.value);
      selectedObservation.value = latestPointForSelection(
        response,
        metricCode.value,
        observedAt.value ?? selectedPlot.value.observed_at,
      );
    } catch (currentError) {
      if (requestId === detailRequestId) {
        plotTrend.value = undefined;
        selectedObservation.value = undefined;
        trendError.value = getMapApiErrorMessage(currentError, '地块趋势查询失败，请稍后重试。');
      }
    } finally {
      if (requestId === detailRequestId) {
        detailLoading.value = false;
        trendLoading.value = false;
      }
    }
  }

  watch(metricCode, async () => {
    suppressObservedDateReload = true;
    observedDate.value = undefined;
    selectedObservation.value = undefined;
    plotTrend.value = undefined;
    trendError.value = '';
    error.value = '';
    try {
      await loadDates();
      await loadLayers();
      await loadSelectedPlotSeries();
    } catch (currentError) {
      error.value = getMapApiErrorMessage(currentError, '指标切换后数据加载失败，请检查后端日期和地图接口。');
    } finally {
      suppressObservedDateReload = false;
    }
  });

  watch(region, () => {
    selectedPlot.value = undefined;
    selectedObservation.value = undefined;
    plotTrend.value = undefined;
    trendError.value = '';
    void loadLayers();
  });

  watch(observedAt, async () => {
    if (suppressObservedDateReload) {
      return;
    }

    selectedObservation.value = undefined;
    trendError.value = '';
    await loadLayers();
    await loadSelectedPlotSeries();
  });

  return {
    region,
    metricCode,
    observedDate,
    observedAt,
    metricOptions,
    availableDates,
    featureCollection,
    mapLayers,
    selectedMetricOption,
    selectedPlot,
    selectedPlotId,
    selectedObservation,
    plotTrend,
    loading,
    detailLoading,
    trendLoading,
    error,
    trendError,
    loadInitialData,
    loadLayers,
    selectPlot,
  };
}
