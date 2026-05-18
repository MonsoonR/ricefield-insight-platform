from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.core.metric_dictionary import METRIC_DICTIONARY, get_metric_by_code
from app.schemas.data_model import (
    DataQualityIssue,
    DataSource,
    Metric,
    MetricObservation,
    ObservationBatch,
    Plot,
)
from app.schemas.mvp_api import (
    AnalysisQuery,
    CorrelationResponse,
    GeoJsonLayer,
    MapLayersQuery,
    MapLayersResponse,
    MapLegend,
    MetricCompareItem,
    MetricCompareResponse,
    MetricSeries,
    MetricsResponse,
    PlotListQuery,
    PlotMetricSnapshot,
    PlotSeriesQuery,
    PlotSeriesResponse,
    PlotSummaryResponse,
    PlotsResponse,
    RegionStatus,
    ScenarioOverviewResponse,
    ScenariosResponse,
    SeriesPoint,
    TwinStatCard,
    WarningItem,
    WarningsResponse,
)
from app.services.demo_data import (
    DEMO_CREATED_AT,
    DEMO_SCENARIO_ID,
    build_demo_data_bundle,
)


QUALITY_FLAG_ORDER = ("error", "missing", "normal", "outlier")
NO_DATA_COLOR = "#D9D9D9"
MISSING_COLOR = "#BFBFBF"
OUTLIER_COLOR = "#FA8C16"
ERROR_COLOR = "#D4380D"
NORMAL_COLOR = "#52C41A"
DEFAULT_SCENARIO_ID = DEMO_SCENARIO_ID
DEFAULT_SCENARIO_NAME = "稻田数字孪生演示场景 2025"
DEFAULT_SCENARIO_CREATED_AT = DEMO_CREATED_AT
DEFAULT_METRIC_CODE = "crop_growth"


@dataclass(frozen=True)
class MvpDataSnapshot:
    metrics: list[Metric]
    plots: list[Plot]
    observations: list[MetricObservation]
    observation_batches: list[ObservationBatch]
    data_sources: list[DataSource]
    quality_issues: list[DataQualityIssue]


class MvpDataStore:
    def __init__(
        self,
        *,
        geojson_dir: str | Path | None = None,
        observations_dir: str | Path | None = None,
    ) -> None:
        self.geojson_dir = Path(geojson_dir) if geojson_dir is not None else None
        self.observations_dir = Path(observations_dir) if observations_dir is not None else None
        self._snapshot: MvpDataSnapshot | None = None

    def get_snapshot(self) -> MvpDataSnapshot:
        if self._snapshot is None:
            self._snapshot = self._load_snapshot()
        return self._snapshot

    def list_scenarios(self) -> ScenariosResponse:
        scenario = self.get_current_scenario()
        return ScenariosResponse(
            items=[scenario],
            total=1,
            current_scenario_id=DEFAULT_SCENARIO_ID,
        )

    def get_current_scenario(self):
        return self.get_scenario(DEFAULT_SCENARIO_ID)

    def get_scenario(self, scenario_id: str):
        if scenario_id != DEFAULT_SCENARIO_ID:
            return None
        return build_demo_data_bundle().scenario

    def get_scenario_overview(self, scenario_id: str | None = None) -> ScenarioOverviewResponse:
        scenario = self.get_scenario(scenario_id or DEFAULT_SCENARIO_ID)
        if scenario is None:
            raise ValueError(scenario_id or "")

        snapshot = self.get_snapshot()
        dates = self.list_dates(metric_code=DEFAULT_METRIC_CODE)
        quality_counts = _quality_counts(snapshot.observations)
        warning_total = sum(
            count for flag, count in quality_counts.items() if flag in {"missing", "outlier", "error"}
        )
        start_date = dates[0]
        end_date = dates[-1]
        return ScenarioOverviewResponse(
            scenario=scenario,
            stat_cards=[
                TwinStatCard(label="地块数量", value=str(len(snapshot.plots)), note="程序生成示例地块"),
                TwinStatCard(label="指标数量", value=str(len(snapshot.metrics)), note="数字孪生指标字典"),
                TwinStatCard(
                    label="观测天数",
                    value=str(len(dates)),
                    note=f"{start_date.isoformat()} 至 {end_date.isoformat()}",
                ),
                TwinStatCard(label="预警数量", value=str(warning_total), note="缺失、异常和突变提示"),
            ],
            health_score=max(0, 100 - warning_total - 2),
            default_metric_code=DEFAULT_METRIC_CODE,
            default_observed_at=end_date,
            quality_counts=quality_counts,
            region_status=self._region_status(snapshot),
        )

    def list_metrics(self) -> MetricsResponse:
        metrics = self.get_snapshot().metrics
        return MetricsResponse(items=metrics, total=len(metrics))

    def list_plots(self, query: PlotListQuery) -> PlotsResponse:
        plots = self.get_snapshot().plots
        if query.region:
            plots = [plot for plot in plots if plot.region == query.region]
        if query.status:
            plots = [plot for plot in plots if plot.status == query.status]
        return PlotsResponse(items=plots, total=len(plots))

    def list_dates(self, metric_code: str | None = None, plot_id: str | None = None) -> list[date]:
        observations = self._filter_observations(metric_code=metric_code, plot_id=plot_id)
        return sorted({record.observed_at for record in observations})

    def get_plot(self, plot_id: str) -> Plot | None:
        return next((plot for plot in self.get_snapshot().plots if plot.plot_id == plot_id), None)

    def get_map_layers(self, query: MapLayersQuery) -> MapLayersResponse:
        snapshot = self.get_snapshot()
        plots = snapshot.plots
        if query.region:
            plots = [plot for plot in plots if plot.region == query.region]

        observations_by_plot = self._latest_observations_by_plot(
            metric_code=query.metric_code,
            observed_at=query.observed_at,
        )
        metric = get_metric_by_code(query.metric_code) if query.metric_code else None
        features = [
            self._plot_feature(plot, observations_by_plot.get(plot.plot_id), metric)
            for plot in plots
        ]
        layer = GeoJsonLayer(
            layer_id="plots",
            layer_name="地块边界",
            layer_type="geojson",
            feature_collection={"type": "FeatureCollection", "features": features},
        )
        return MapLayersResponse(
            layers=[layer],
            metric_code=query.metric_code,
            observed_at=query.observed_at,
            legend=MapLegend(
                metric_code=metric.metric_code if metric else None,
                unit=metric.unit if metric else None,
                color_scale=metric.color_scale if metric else None,
            ),
        )

    def get_plot_summary(self, plot_id: str) -> PlotSummaryResponse | None:
        plot = self.get_plot(plot_id)
        if plot is None:
            return None

        observations = self._filter_observations(plot_id=plot_id)
        latest = self._latest_observations_by_metric(observations)
        quality_counts = _quality_counts(observations)
        return PlotSummaryResponse(
            plot=plot,
            latest_observations=[self._snapshot_from_observation(record) for record in latest],
            quality_counts={flag: count for flag, count in quality_counts.items() if count},
            batch_ids=sorted({record.batch_id for record in observations}),
        )

    def get_plot_series(
        self,
        plot_id: str,
        query: PlotSeriesQuery,
    ) -> PlotSeriesResponse | None:
        plot = self.get_plot(plot_id)
        if plot is None:
            return None

        observations = self._filter_observations(
            plot_id=plot_id,
            metric_code=query.metric_code,
            start_date=query.start_date,
            end_date=query.end_date,
        )
        grouped: dict[str, list[MetricObservation]] = {}
        for record in observations:
            grouped.setdefault(record.metric_code, []).append(record)

        series = []
        for metric_code in sorted(grouped):
            metric = get_metric_by_code(metric_code)
            if metric is None:
                continue
            records = sorted(grouped[metric_code], key=_observation_sort_key)
            series.append(
                MetricSeries(
                    metric_code=metric.metric_code,
                    metric_name=metric.metric_name,
                    unit=metric.unit,
                    points=[self._series_point(record) for record in records],
                )
            )
        return PlotSeriesResponse(plot=plot, series=series)

    def get_correlation_placeholder(self, query: AnalysisQuery) -> CorrelationResponse:
        return CorrelationResponse(
            status="placeholder",
            message="第一阶段暂不计算相关性，当前返回稳定占位结构。",
            matrix=[],
            sample_count=0,
            filters=query,
        )

    def get_metric_compare(self, query: AnalysisQuery) -> MetricCompareResponse:
        metric_code = query.metric_code or DEFAULT_METRIC_CODE
        metric = get_metric_by_code(metric_code)
        if metric is None:
            raise ValueError(metric_code)
        dates = self.list_dates(metric_code=metric_code)
        observed_at = query.observed_at or dates[-1]
        observations_by_plot = self._latest_observations_by_plot(
            metric_code=metric_code,
            observed_at=observed_at,
        )
        plots = self.get_snapshot().plots
        if query.region:
            plots = [plot for plot in plots if plot.region == query.region]

        rows: list[tuple[Plot, MetricObservation]] = [
            (plot, observations_by_plot[plot.plot_id])
            for plot in plots
            if plot.plot_id in observations_by_plot
        ]
        rows.sort(key=lambda row: (row[1].value is None, -(row[1].value or 0), row[0].plot_code))
        items = [
            MetricCompareItem(
                rank=index + 1,
                plot_id=plot.plot_id,
                plot_code=plot.plot_code,
                plot_name=plot.plot_name,
                region=plot.region,
                value=record.value,
                unit=record.unit,
                quality_flag=record.quality_flag,
                observed_at=record.observed_at,
            )
            for index, (plot, record) in enumerate(rows)
        ]
        return MetricCompareResponse(
            metric_code=metric.metric_code,
            metric_name=metric.metric_name,
            observed_at=observed_at,
            items=items,
            total=len(items),
        )

    def get_warnings(self, query: AnalysisQuery) -> WarningsResponse:
        snapshot = self.get_snapshot()
        plots_by_id = {plot.plot_id: plot for plot in snapshot.plots}
        issues = snapshot.quality_issues
        if query.metric_code:
            issues = [issue for issue in issues if issue.metric_code == query.metric_code]
        if query.start_date:
            issues = [issue for issue in issues if issue.observed_at and issue.observed_at >= query.start_date]
        if query.end_date:
            issues = [issue for issue in issues if issue.observed_at and issue.observed_at <= query.end_date]
        if query.region:
            issues = [
                issue
                for issue in issues
                if issue.plot_id and plots_by_id[issue.plot_id].region == query.region
            ]

        items: list[WarningItem] = []
        for issue in sorted(issues, key=lambda item: (item.observed_at or date.min, item.plot_code or "")):
            if not issue.plot_id or not issue.plot_code or not issue.metric_code or not issue.observed_at:
                continue
            plot = plots_by_id[issue.plot_id]
            metric = get_metric_by_code(issue.metric_code)
            items.append(
                WarningItem(
                    warning_id=issue.issue_id,
                    scenario_id=issue.scenario_id,
                    warning_type=issue.issue_type,
                    severity=issue.severity,
                    plot_id=issue.plot_id,
                    plot_code=issue.plot_code,
                    plot_name=plot.plot_name,
                    region=plot.region,
                    metric_code=issue.metric_code,
                    metric_name=metric.metric_name if metric else issue.metric_code,
                    observed_at=issue.observed_at,
                    value=issue.value,
                    message=issue.message,
                )
            )
        return WarningsResponse(items=items, total=len(items), filters=query)

    def _load_snapshot(self) -> MvpDataSnapshot:
        bundle = build_demo_data_bundle()
        return MvpDataSnapshot(
            metrics=list(METRIC_DICTIONARY),
            plots=bundle.plots,
            observations=bundle.observations,
            observation_batches=[bundle.observation_batch],
            data_sources=bundle.data_sources,
            quality_issues=bundle.quality_issues,
        )

    def _filter_observations(
        self,
        *,
        plot_id: str | None = None,
        metric_code: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MetricObservation]:
        records = self.get_snapshot().observations
        if plot_id:
            records = [record for record in records if record.plot_id == plot_id]
        if metric_code:
            records = [record for record in records if record.metric_code == metric_code]
        if start_date:
            records = [record for record in records if record.observed_at >= start_date]
        if end_date:
            records = [record for record in records if record.observed_at <= end_date]
        return records

    def _latest_observations_by_plot(
        self,
        *,
        metric_code: str | None,
        observed_at: date | None,
    ) -> dict[str, MetricObservation]:
        records = self._filter_observations(metric_code=metric_code)
        if observed_at:
            records = [record for record in records if record.observed_at == observed_at]

        latest_by_plot: dict[str, MetricObservation] = {}
        for record in records:
            current = latest_by_plot.get(record.plot_id)
            if current is None or _observation_sort_key(record) > _observation_sort_key(current):
                latest_by_plot[record.plot_id] = record
        return latest_by_plot

    def _latest_observations_by_metric(
        self,
        observations: list[MetricObservation],
    ) -> list[MetricObservation]:
        latest_by_metric: dict[str, MetricObservation] = {}
        for record in observations:
            current = latest_by_metric.get(record.metric_code)
            if current is None or _observation_sort_key(record) > _observation_sort_key(current):
                latest_by_metric[record.metric_code] = record
        return [latest_by_metric[metric_code] for metric_code in sorted(latest_by_metric)]

    def _plot_feature(
        self,
        plot: Plot,
        observation: MetricObservation | None,
        metric: Metric | None,
    ) -> dict:
        properties = {
            "plot_id": plot.plot_id,
            "plot_code": plot.plot_code,
            "plot_name": plot.plot_name,
            "region": plot.region,
            "status": plot.status,
            "metric_code": observation.metric_code if observation else metric.metric_code if metric else None,
            "value": observation.value if observation else None,
            "unit": observation.unit if observation else metric.unit if metric else None,
            "observed_at": observation.observed_at.isoformat() if observation else None,
            "quality_flag": observation.quality_flag if observation else "missing",
            "fill_color": _fill_color(observation),
            "batch_id": observation.batch_id if observation else None,
            "data_source_id": observation.data_source_id if observation else None,
        }
        return {"type": "Feature", "geometry": plot.geometry, "properties": properties}

    def _snapshot_from_observation(self, record: MetricObservation) -> PlotMetricSnapshot:
        metric = get_metric_by_code(record.metric_code)
        metric_name = metric.metric_name if metric else record.metric_code
        return PlotMetricSnapshot(
            metric_code=record.metric_code,
            metric_name=metric_name,
            value=record.value,
            unit=record.unit,
            observed_at=record.observed_at,
            quality_flag=record.quality_flag,
            batch_id=record.batch_id,
            data_source_id=record.data_source_id,
        )

    def _series_point(self, record: MetricObservation) -> SeriesPoint:
        return SeriesPoint(
            observed_at=record.observed_at,
            value=record.value,
            quality_flag=record.quality_flag,
            batch_id=record.batch_id,
            data_source_id=record.data_source_id,
        )

    def _region_status(self, snapshot: MvpDataSnapshot) -> list[RegionStatus]:
        regions = sorted({plot.region for plot in snapshot.plots if plot.region})
        result = []
        for region in regions:
            region_plots = [plot for plot in snapshot.plots if plot.region == region]
            plot_ids = {plot.plot_id for plot in region_plots}
            warning_count = sum(
                1 for issue in snapshot.quality_issues if issue.plot_id in plot_ids
            )
            result.append(
                RegionStatus(
                    region=region,
                    plot_count=len(region_plots),
                    warning_count=warning_count,
                )
            )
        return result


_default_store = MvpDataStore()


def get_default_store() -> MvpDataStore:
    return _default_store


def _quality_counts(observations: list[MetricObservation]) -> dict[str, int]:
    return {
        flag: sum(1 for record in observations if record.quality_flag == flag)
        for flag in QUALITY_FLAG_ORDER
    }


def _observation_sort_key(record: MetricObservation) -> tuple:
    return (record.observed_at, record.batch_id)


def _fill_color(observation: MetricObservation | None) -> str:
    if observation is None or observation.value is None:
        return NO_DATA_COLOR
    if observation.quality_flag == "missing":
        return MISSING_COLOR
    if observation.quality_flag == "outlier":
        return OUTLIER_COLOR
    if observation.quality_flag == "error":
        return ERROR_COLOR
    return NORMAL_COLOR
