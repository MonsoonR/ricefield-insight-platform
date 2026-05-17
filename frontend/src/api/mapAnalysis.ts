import {
  fetchDates,
  fetchMapLayers,
  fetchMetrics,
  fetchPlotSeries,
} from './index';

import type { MetricOption } from '@/types/common';

export { fetchMapLayers, fetchPlotSeries };

export async function fetchMetricOptions() {
  const data = await fetchMetrics();
  return data.items.map<MetricOption>((item) => ({
    label: item.metric_name,
    value: item.metric_code,
    unit: item.unit,
    category: item.category,
  }));
}

export async function fetchObservationDates(metricCode: string) {
  const data = await fetchDates({ metricCode });
  return data.items;
}
