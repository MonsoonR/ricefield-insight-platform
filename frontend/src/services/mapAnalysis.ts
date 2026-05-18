import type { PlotMetricSeries, PlotSeriesResponse } from '@/types/mapAnalysis';

export type MapRegionCode = 'all' | 'east' | 'west';

export type MapQualityFlag = 'normal' | 'missing' | 'outlier' | 'error' | string;

export interface MapMetric {
  metric_code: string;
  metric_name: string;
  unit: string;
  color_scale?: string | null;
}

export interface MapFeatureProperties {
  plot_id?: string;
  plot_code?: string;
  plot_name?: string;
  region?: string;
  status?: string;
  metric_code?: string | null;
  value?: number | string | null;
  unit?: string | null;
  observed_at?: string | null;
  quality_flag?: MapQualityFlag | null;
  fill_color?: string | null;
}

export interface MapFeature {
  type: 'Feature';
  geometry: {
    type: string;
    coordinates: unknown;
  };
  properties: MapFeatureProperties;
}

export interface MapFeatureCollection {
  type: 'FeatureCollection';
  features: MapFeature[];
}

export interface MapLayer {
  layer_id: string;
  layer_name: string;
  layer_type: 'geojson';
  feature_collection: MapFeatureCollection;
}

export interface MapLegend {
  metric_code?: string | null;
  unit?: string | null;
  color_scale?: string | null;
  no_data_color: string;
  missing_color: string;
  outlier_color: string;
  error_color: string;
}

export interface MapLayersResponse {
  layers: MapLayer[];
  metric_code?: string | null;
  observed_at?: string | null;
  legend: MapLegend;
}

export interface MapLayerFilters {
  region?: MapRegionCode;
  metricCode?: string;
  observedAt?: string;
}

interface ApiErrorLike {
  response?: {
    data?: {
      detail?: unknown;
      message?: unknown;
    };
  };
}

export interface PlotVisualStyle {
  fillColor: string;
  fillOpacity: number;
  outlineColor: string;
  outlineWidth: number;
  dashedOutline: boolean;
  pulse: boolean;
  status: 'normal' | 'missing' | 'abnormal';
}

export type PlotVisualStatus = PlotVisualStyle['status'];

const REGION_TO_API: Record<Exclude<MapRegionCode, 'all'>, string> = {
  east: '试验一区',
  west: '试验二区',
};

const NORMAL_OUTLINE = '#237804';
const MISSING_OUTLINE = '#8C8C8C';
const ABNORMAL_OUTLINE = '#CF1322';
const DEFAULT_NORMAL_FILL = '#52C41A';
const DEFAULT_MISSING_FILL = '#D9D9D9';
const DEFAULT_ERROR_FILL = '#D4380D';
const ABNORMAL_PLOT_STATUSES = new Set(['duplicate', 'invalid_code', 'error', 'abnormal']);
const NO_DATA_PLOT_STATUSES = new Set(['no_data', 'empty']);

export function toApiRegion(region: MapRegionCode | undefined) {
  if (!region || region === 'all') {
    return undefined;
  }

  return REGION_TO_API[region];
}

export function buildMapLayerParams(filters: MapLayerFilters) {
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

  return params;
}

export function resolvePlotVisualStatus(properties: MapFeatureProperties): PlotVisualStatus {
  const qualityFlag = properties.quality_flag;
  const plotStatus = properties.status?.toLowerCase();
  const hasValue = properties.value !== null && properties.value !== undefined && properties.value !== '';

  if (
    qualityFlag === 'outlier'
    || qualityFlag === 'error'
    || (plotStatus !== undefined && ABNORMAL_PLOT_STATUSES.has(plotStatus))
  ) {
    return 'abnormal';
  }

  if (
    !hasValue
    || qualityFlag === 'missing'
    || (plotStatus !== undefined && NO_DATA_PLOT_STATUSES.has(plotStatus))
  ) {
    return 'missing';
  }

  return 'normal';
}

export function resolvePlotVisualStyle(properties: MapFeatureProperties): PlotVisualStyle {
  const qualityFlag = properties.quality_flag;
  const visualStatus = resolvePlotVisualStatus(properties);

  if (visualStatus === 'missing') {
    return {
      fillColor: properties.fill_color ?? DEFAULT_MISSING_FILL,
      fillOpacity: 0.32,
      outlineColor: MISSING_OUTLINE,
      outlineWidth: 1.8,
      dashedOutline: true,
      pulse: false,
      status: 'missing',
    };
  }

  if (visualStatus === 'abnormal') {
    return {
      fillColor: qualityFlag === 'outlier' && properties.fill_color
        ? properties.fill_color
        : DEFAULT_ERROR_FILL,
      fillOpacity: 0.66,
      outlineColor: ABNORMAL_OUTLINE,
      outlineWidth: 3,
      dashedOutline: false,
      pulse: true,
      status: 'abnormal',
    };
  }

  return {
    fillColor: properties.fill_color ?? DEFAULT_NORMAL_FILL,
    fillOpacity: 0.56,
    outlineColor: NORMAL_OUTLINE,
    outlineWidth: 1.6,
    dashedOutline: false,
    pulse: false,
    status: 'normal',
  };
}

export function latestPointForSelection(
  response: PlotSeriesResponse | undefined,
  metricCode: string,
  observedAt?: string | null,
) {
  const series = response?.series.find((item) => item.metric_code === metricCode);
  if (!series || series.points.length === 0) {
    return undefined;
  }

  if (observedAt) {
    const exactPoint = series.points.find((point) => point.observed_at === observedAt);
    if (exactPoint) {
      return exactPoint;
    }
  }

  const sortedPoints = [...series.points].sort((a, b) => a.observed_at.localeCompare(b.observed_at));
  return sortedPoints[sortedPoints.length - 1];
}

export function trendSeriesForMetric(
  response: PlotSeriesResponse | undefined,
  metricCode: string,
): PlotMetricSeries | undefined {
  const series = response?.series.find((item) => item.metric_code === metricCode);
  if (!series) {
    return undefined;
  }

  return {
    ...series,
    points: [...series.points].sort((a, b) => a.observed_at.localeCompare(b.observed_at)),
  };
}

export function getMapApiErrorMessage(error: unknown, fallback: string) {
  const apiError = error as ApiErrorLike;
  const detail = apiError.response?.data?.detail ?? apiError.response?.data?.message;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  return fallback;
}
