from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel

from app.schemas.data_model import (
    Metric,
    Plot,
    QualityFlag,
    ScenarioDateRange,
    TwinScenario,
)


class ScenariosResponse(BaseModel):
    items: list[TwinScenario]
    total: int
    current_scenario_id: str


class ScenarioQuery(BaseModel):
    scenario_id: str | None = None


class MetricsResponse(BaseModel):
    items: list[Metric]
    total: int


class PlotListQuery(BaseModel):
    scenario_id: str | None = None
    region: str | None = None
    status: str | None = None


class PlotsResponse(BaseModel):
    items: list[Plot]
    total: int


class DatesQuery(BaseModel):
    scenario_id: str | None = None
    metric_code: str | None = None
    plot_id: str | None = None


class DatesResponse(BaseModel):
    items: list[date]
    total: int


class TwinStatCard(BaseModel):
    label: str
    value: str
    note: str


class RegionStatus(BaseModel):
    region: str
    plot_count: int
    warning_count: int


class ScenarioOverviewResponse(BaseModel):
    scenario: TwinScenario
    stat_cards: list[TwinStatCard]
    health_score: int
    default_metric_code: str
    default_observed_at: date
    quality_counts: dict[str, int]
    region_status: list[RegionStatus]


class MapLayersQuery(BaseModel):
    scenario_id: str | None = None
    metric_code: str | None = None
    observed_at: date | None = None
    region: str | None = None


class MapLegend(BaseModel):
    metric_code: str | None = None
    unit: str | None = None
    color_scale: str | None = None
    no_data_color: str = "#D9D9D9"
    missing_color: str = "#BFBFBF"
    outlier_color: str = "#FA8C16"
    error_color: str = "#D4380D"


class GeoJsonLayer(BaseModel):
    layer_id: str
    layer_name: str
    layer_type: Literal["geojson"]
    feature_collection: dict[str, Any]


class MapLayersResponse(BaseModel):
    layers: list[GeoJsonLayer]
    metric_code: str | None = None
    observed_at: date | None = None
    legend: MapLegend


class PlotMetricSnapshot(BaseModel):
    metric_code: str
    metric_name: str
    value: float | int | None
    unit: str
    observed_at: date
    quality_flag: QualityFlag
    batch_id: str
    data_source_id: str


class PlotSummaryResponse(BaseModel):
    plot: Plot
    latest_observations: list[PlotMetricSnapshot]
    quality_counts: dict[str, int]
    batch_ids: list[str]


class PlotSeriesQuery(BaseModel):
    scenario_id: str | None = None
    metric_code: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class SeriesPoint(BaseModel):
    observed_at: date
    value: float | int | None
    quality_flag: QualityFlag
    batch_id: str
    data_source_id: str


class MetricSeries(BaseModel):
    metric_code: str
    metric_name: str
    unit: str
    points: list[SeriesPoint]


class PlotSeriesResponse(BaseModel):
    plot: Plot
    series: list[MetricSeries]


class AnalysisQuery(BaseModel):
    scenario_id: str | None = None
    metric_code: str | None = None
    observed_at: date | None = None
    region: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class CorrelationResponse(BaseModel):
    status: Literal["placeholder"]
    message: str
    matrix: list[dict[str, Any]]
    sample_count: int
    filters: AnalysisQuery


class MetricCompareItem(BaseModel):
    rank: int
    plot_id: str
    plot_code: str
    plot_name: str | None = None
    region: str | None = None
    value: float | int | None
    unit: str
    quality_flag: QualityFlag
    observed_at: date


class MetricCompareResponse(BaseModel):
    metric_code: str
    metric_name: str
    observed_at: date
    items: list[MetricCompareItem]
    total: int


class WarningItem(BaseModel):
    warning_id: str
    scenario_id: str
    warning_type: QualityFlag
    severity: Literal["info", "warning", "error"]
    plot_id: str
    plot_code: str
    plot_name: str | None = None
    region: str | None = None
    metric_code: str
    metric_name: str
    observed_at: date
    value: float | int | None = None
    message: str


class WarningsResponse(BaseModel):
    items: list[WarningItem]
    total: int
    filters: AnalysisQuery
