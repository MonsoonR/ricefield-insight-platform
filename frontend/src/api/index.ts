import { http } from './http';

import type {
  ApiListResponse,
  CorrelationResponse,
  MapLayersResponse,
  Metric,
  MetricCompareResponse,
  Plot,
  PlotSeriesResponse,
  PlotSummaryResponse,
  RegionCode,
  ScenarioOverviewResponse,
  TwinScenario,
  WarningsResponse,
} from '@/types/api';

export { getApiErrorMessage, http } from './http';

const REGION_TO_API: Record<Exclude<RegionCode, 'all'>, string> = {
  east: '试验一区',
  west: '试验二区',
};

export function toApiRegion(region?: RegionCode) {
  if (!region || region === 'all') {
    return undefined;
  }
  return REGION_TO_API[region];
}

export async function fetchHealth() {
  const { data } = await http.get<{ status: string; message: string }>('/health');
  return data;
}

export async function fetchCurrentScenario() {
  const { data } = await http.get<TwinScenario>('/scenarios/current');
  return data;
}

export async function fetchScenarioOverview(scenarioId = 'demo-ricefield-2025') {
  const { data } = await http.get<ScenarioOverviewResponse>(
    `/scenarios/${encodeURIComponent(scenarioId)}/overview`,
  );
  return data;
}

export async function fetchMetrics() {
  const { data } = await http.get<ApiListResponse<Metric>>('/metrics');
  return data;
}

export async function fetchPlots(filters: { region?: RegionCode; status?: string } = {}) {
  const params: Record<string, string> = {};
  const region = toApiRegion(filters.region);
  if (region) {
    params.region = region;
  }
  if (filters.status) {
    params.status = filters.status;
  }
  const { data } = await http.get<ApiListResponse<Plot>>('/plots', { params });
  return data;
}

export async function fetchDates(filters: { metricCode?: string; plotId?: string } = {}) {
  const params: Record<string, string> = {};
  if (filters.metricCode) {
    params.metric_code = filters.metricCode;
  }
  if (filters.plotId) {
    params.plot_id = filters.plotId;
  }
  const { data } = await http.get<ApiListResponse<string>>('/dates', { params });
  return data;
}

export async function fetchMapLayers(filters: {
  region?: RegionCode;
  metricCode?: string;
  observedAt?: string;
} = {}) {
  const params: Record<string, string> = {};
  const region = toApiRegion(filters.region);
  if (region) {
    params.region = region;
  }
  if (filters.metricCode) {
    params.metric_code = filters.metricCode;
  }
  if (filters.observedAt) {
    params.observed_at = filters.observedAt;
  }

  const { data } = await http.get<MapLayersResponse>('/map/layers', { params });
  return data;
}

export async function fetchPlotSummary(plotId: string) {
  const { data } = await http.get<PlotSummaryResponse>(`/plots/${encodeURIComponent(plotId)}/summary`);
  return data;
}

export async function fetchPlotSeries(filters: {
  plotId: string;
  metricCode?: string;
  startDate?: string | null;
  endDate?: string | null;
}) {
  const params: Record<string, string> = {};
  if (filters.metricCode) {
    params.metric_code = filters.metricCode;
  }
  if (filters.startDate) {
    params.start_date = filters.startDate;
  }
  if (filters.endDate) {
    params.end_date = filters.endDate;
  }

  const { data } = await http.get<PlotSeriesResponse>(
    `/plots/${encodeURIComponent(filters.plotId)}/series`,
    { params },
  );
  return data;
}

export async function fetchCorrelation(filters: {
  region?: RegionCode;
  metricCode?: string;
  startDate?: string | null;
  endDate?: string | null;
} = {}) {
  const params = buildAnalysisParams(filters);
  const { data } = await http.get<CorrelationResponse>('/analysis/correlation', { params });
  return data;
}

export async function fetchMetricCompare(filters: {
  region?: RegionCode;
  metricCode?: string;
  observedAt?: string | null;
} = {}) {
  const params = buildAnalysisParams(filters);
  const { data } = await http.get<MetricCompareResponse>('/analysis/metric-compare', { params });
  return data;
}

export async function fetchWarnings(filters: {
  region?: RegionCode;
  metricCode?: string;
  startDate?: string | null;
  endDate?: string | null;
} = {}) {
  const params = buildAnalysisParams(filters);
  const { data } = await http.get<WarningsResponse>('/analysis/warnings', { params });
  return data;
}

function buildAnalysisParams(filters: {
  region?: RegionCode;
  metricCode?: string;
  observedAt?: string | null;
  startDate?: string | null;
  endDate?: string | null;
}) {
  const params: Record<string, string> = {};
  const region = toApiRegion(filters.region);
  if (region) {
    params.region = region;
  }
  if (filters.metricCode) {
    params.metric_code = filters.metricCode;
  }
  if (filters.observedAt) {
    params.observed_at = filters.observedAt;
  }
  if (filters.startDate) {
    params.start_date = filters.startDate;
  }
  if (filters.endDate) {
    params.end_date = filters.endDate;
  }
  return params;
}
