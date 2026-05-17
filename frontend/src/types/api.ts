export type RegionCode = 'all' | 'east' | 'west';
export type ApiRegionName = '试验一区' | '试验二区';
export type QualityFlag = 'normal' | 'missing' | 'outlier' | 'error' | string;
export type PlaceholderStatus = 'placeholder' | string;

export interface ApiListResponse<T> {
  items: T[];
  total: number;
}

export interface DateRange {
  start_date?: string | null;
  end_date?: string | null;
}

export interface TwinScenario {
  scenario_id: string;
  scenario_name: string;
  description: string;
  data_mode: string;
  plot_count: number;
  metric_count: number;
  date_range: DateRange;
  created_at: string;
}

export interface TwinStatCard {
  label: string;
  value: string;
  note: string;
}

export interface RegionStatus {
  region: string;
  plot_count: number;
  warning_count: number;
}

export interface ScenarioOverviewResponse {
  scenario: TwinScenario;
  stat_cards: TwinStatCard[];
  health_score: number;
  default_metric_code: string;
  default_observed_at: string;
  quality_counts: Record<string, number>;
  region_status: RegionStatus[];
}

export interface Metric {
  metric_code: string;
  metric_name: string;
  category?: string;
  unit: string;
  value_type?: string;
  precision?: number;
  normal_range?: {
    min?: number | null;
    max?: number | null;
  } | null;
  color_scale?: string | null;
  description?: string;
  source_type?: string;
}

export interface Plot {
  plot_id: string;
  plot_code: string;
  aliases?: string[];
  plot_name: string;
  region: string;
  geometry?: GeoJsonGeometry;
  status: string;
}

export interface GeoJsonGeometry {
  type: string;
  coordinates: unknown;
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
  quality_flag?: QualityFlag | null;
  fill_color?: string | null;
  batch_id?: string | null;
  data_source_id?: string | null;
}

export interface MapFeature {
  type: 'Feature';
  geometry: GeoJsonGeometry;
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

export interface PlotMetricSnapshot {
  metric_code: string;
  metric_name: string;
  value: number | string | null;
  unit: string;
  observed_at: string;
  quality_flag: QualityFlag;
  batch_id: string;
  data_source_id: string;
}

export interface PlotSummaryResponse {
  plot: Plot;
  latest_observations: PlotMetricSnapshot[];
  quality_counts: Record<string, number>;
  batch_ids: string[];
}

export interface PlotSeriesPoint {
  observed_at: string;
  value: number | string | null;
  quality_flag: QualityFlag;
  batch_id: string;
  data_source_id: string;
}

export interface MetricSeries {
  metric_code: string;
  metric_name: string;
  unit: string;
  points: PlotSeriesPoint[];
}

export interface PlotSeriesResponse {
  plot: Plot;
  series: MetricSeries[];
}

export interface AnalysisFilters {
  metric_code?: string | null;
  observed_at?: string | null;
  region?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface CorrelationResponse {
  status: PlaceholderStatus;
  message: string;
  matrix: Array<Record<string, unknown>>;
  sample_count: number;
  filters: AnalysisFilters;
}

export interface MetricCompareItem {
  rank: number;
  plot_id: string;
  plot_code: string;
  plot_name?: string | null;
  region?: string | null;
  value: number | string | null;
  unit: string;
  quality_flag: QualityFlag;
  observed_at: string;
}

export interface MetricCompareResponse {
  metric_code: string;
  metric_name: string;
  observed_at: string;
  items: MetricCompareItem[];
  total: number;
}

export interface WarningItem {
  warning_id: string;
  scenario_id: string;
  warning_type: QualityFlag;
  severity: 'info' | 'warning' | 'error' | string;
  plot_id: string;
  plot_code: string;
  plot_name?: string | null;
  region?: string | null;
  metric_code: string;
  metric_name: string;
  observed_at: string;
  value: number | string | null;
  message: string;
}

export interface WarningsResponse {
  items: WarningItem[];
  total: number;
  filters: AnalysisFilters;
}
