from __future__ import annotations

import json
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.metric_dictionary import get_metric_by_code
from app.models import ImportIssueModel, MetricModel, MetricObservationModel, PlotModel
from app.schemas.data_model import Metric, MetricObservation, NormalRange, Plot
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
    ScenarioDateRange,
    SeriesPoint,
    TwinScenario,
    TwinStatCard,
    WarningItem,
    WarningsResponse,
)
from app.services.mvp_data import (
    DEFAULT_METRIC_CODE,
    DEFAULT_SCENARIO_CREATED_AT,
    DEFAULT_SCENARIO_ID,
    DEFAULT_SCENARIO_NAME,
    ERROR_COLOR,
    MISSING_COLOR,
    NO_DATA_COLOR,
    NORMAL_COLOR,
    OUTLIER_COLOR,
)


QUALITY_FLAG_ORDER = ("error", "missing", "normal", "outlier")


class DatabaseDataStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_scenarios(self) -> ScenariosResponse:
        scenario = self.get_current_scenario()
        return ScenariosResponse(items=[scenario], total=1, current_scenario_id=DEFAULT_SCENARIO_ID)

    def get_current_scenario(self) -> TwinScenario:
        return self.get_scenario(DEFAULT_SCENARIO_ID)

    def get_scenario(self, scenario_id: str) -> TwinScenario | None:
        if scenario_id != DEFAULT_SCENARIO_ID:
            return None

        plot_count = self.session.scalar(select(func.count()).select_from(PlotModel)) or 0
        metric_count = self.session.scalar(select(func.count()).select_from(MetricModel)) or 0
        start_date = self.session.scalar(select(func.min(MetricObservationModel.observed_at)))
        end_date = self.session.scalar(select(func.max(MetricObservationModel.observed_at)))
        return TwinScenario(
            scenario_id=DEFAULT_SCENARIO_ID,
            scenario_name=DEFAULT_SCENARIO_NAME,
            description="PostGIS 可选正式层，根据标准化表中的地块、指标和观测记录生成数字孪生视图。",
            data_mode="postgis",
            plot_count=plot_count,
            metric_count=metric_count,
            date_range=ScenarioDateRange(start_date=start_date, end_date=end_date),
            created_at=DEFAULT_SCENARIO_CREATED_AT,
        )

    def get_scenario_overview(self, scenario_id: str | None = None) -> ScenarioOverviewResponse:
        scenario = self.get_scenario(scenario_id or DEFAULT_SCENARIO_ID)
        if scenario is None:
            raise ValueError(scenario_id or "")

        dates = self.list_dates(metric_code=DEFAULT_METRIC_CODE)
        start_date = dates[0] if dates else scenario.date_range.start_date
        end_date = dates[-1] if dates else scenario.date_range.end_date
        quality_counts = self._quality_counts()
        warning_total = sum(
            count for flag, count in quality_counts.items() if flag in {"missing", "outlier", "error"}
        )
        return ScenarioOverviewResponse(
            scenario=scenario,
            stat_cards=[
                TwinStatCard(label="地块数量", value=str(scenario.plot_count), note="PostGIS 标准地块"),
                TwinStatCard(label="指标数量", value=str(scenario.metric_count), note="数字孪生指标字典"),
                TwinStatCard(
                    label="观测天数",
                    value=str(len(dates)),
                    note=f"{start_date} 至 {end_date}" if start_date and end_date else "暂无观测日期",
                ),
                TwinStatCard(label="预警数量", value=str(warning_total), note="缺失、异常和错误提示"),
            ],
            health_score=max(0, 100 - warning_total - 2),
            default_metric_code=DEFAULT_METRIC_CODE,
            default_observed_at=end_date or date.today(),
            quality_counts=quality_counts,
            region_status=self._region_status(),
        )

    def list_metrics(self) -> MetricsResponse:
        rows = self.session.scalars(select(MetricModel).order_by(MetricModel.metric_code)).all()
        metrics = [_metric_schema(row) for row in rows]
        return MetricsResponse(items=metrics, total=len(metrics))

    def list_plots(self, query: PlotListQuery) -> PlotsResponse:
        statement = select(PlotModel).options(selectinload(PlotModel.aliases))
        if query.region:
            statement = statement.where(PlotModel.region == query.region)
        if query.status:
            statement = statement.where(PlotModel.status == query.status)
        rows = self.session.scalars(statement.order_by(PlotModel.plot_id)).all()
        plots = [_plot_schema(row) for row in rows]
        return PlotsResponse(items=plots, total=len(plots))

    def list_dates(self, metric_code: str | None = None, plot_id: str | None = None) -> list[date]:
        statement = select(MetricObservationModel.observed_at).distinct()
        if metric_code:
            statement = statement.where(MetricObservationModel.metric_code == metric_code)
        if plot_id:
            statement = statement.where(MetricObservationModel.plot_id == plot_id)
        return list(self.session.scalars(statement.order_by(MetricObservationModel.observed_at)).all())

    def get_plot(self, plot_id: str) -> Plot | None:
        row = self.session.scalar(
            select(PlotModel).where(PlotModel.plot_id == plot_id).options(selectinload(PlotModel.aliases))
        )
        return _plot_schema(row) if row else None

    def get_map_layers(self, query: MapLayersQuery) -> MapLayersResponse:
        plots_statement = select(PlotModel, func.ST_AsGeoJSON(PlotModel.geometry)).options(
            selectinload(PlotModel.aliases)
        )
        if query.region:
            plots_statement = plots_statement.where(PlotModel.region == query.region)
        plot_rows = self.session.execute(plots_statement.order_by(PlotModel.plot_id)).all()
        observations_by_plot = self._latest_observations_by_plot(
            metric_code=query.metric_code,
            observed_at=query.observed_at,
        )
        metric = get_metric_by_code(query.metric_code) if query.metric_code else None
        features = [
            self._plot_feature(
                _plot_schema(plot, geometry_json=geometry_json),
                observations_by_plot.get(plot.plot_id),
                metric,
            )
            for plot, geometry_json in plot_rows
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

    def get_plot_series(self, plot_id: str, query: PlotSeriesQuery) -> PlotSeriesResponse | None:
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
        plots = self.list_plots(PlotListQuery(region=query.region)).items
        rows = [
            (plot, observations_by_plot[plot.plot_id])
            for plot in plots
            if plot.plot_id in observations_by_plot
        ]
        rows.sort(key=lambda row: (row[1].value is None, -(row[1].value or 0), row[0].plot_code))
        return MetricCompareResponse(
            metric_code=metric.metric_code,
            metric_name=metric.metric_name,
            observed_at=observed_at,
            items=[
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
            ],
            total=len(rows),
        )

    def get_warnings(self, query: AnalysisQuery) -> WarningsResponse:
        observations = self._filter_observations(
            metric_code=query.metric_code,
            start_date=query.start_date,
            end_date=query.end_date,
        )
        plots_by_id = {plot.plot_id: plot for plot in self.list_plots(PlotListQuery()).items}
        warning_records = [
            record
            for record in observations
            if record.quality_flag in {"missing", "outlier", "error"}
            and (not query.region or plots_by_id[record.plot_id].region == query.region)
        ]
        items: list[WarningItem] = []
        for record in warning_records:
            plot = plots_by_id[record.plot_id]
            metric = get_metric_by_code(record.metric_code)
            metric_name = metric.metric_name if metric else record.metric_code
            items.append(
                WarningItem(
                    warning_id=f"warning-{record.id}",
                    scenario_id=DEFAULT_SCENARIO_ID,
                    warning_type=record.quality_flag,
                    severity="warning" if record.quality_flag == "missing" else "error",
                    plot_id=record.plot_id,
                    plot_code=record.plot_code,
                    plot_name=plot.plot_name,
                    region=plot.region,
                    metric_code=record.metric_code,
                    metric_name=metric_name,
                    observed_at=record.observed_at,
                    value=record.value,
                    message=f"{plot.plot_name} 在 {record.observed_at.isoformat()} 的{metric_name}出现预警。",
                )
            )
        items.sort(key=lambda item: (item.observed_at, item.plot_code, item.metric_code))
        return WarningsResponse(items=items, total=len(items), filters=query)

    def _filter_observations(
        self,
        *,
        plot_id: str | None = None,
        metric_code: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MetricObservation]:
        statement = select(MetricObservationModel)
        if plot_id:
            statement = statement.where(MetricObservationModel.plot_id == plot_id)
        if metric_code:
            statement = statement.where(MetricObservationModel.metric_code == metric_code)
        if start_date:
            statement = statement.where(MetricObservationModel.observed_at >= start_date)
        if end_date:
            statement = statement.where(MetricObservationModel.observed_at <= end_date)
        rows = self.session.scalars(statement.order_by(MetricObservationModel.observed_at)).all()
        return [_observation_schema(row) for row in rows]

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

    def _latest_observations_by_metric(self, observations: list[MetricObservation]) -> list[MetricObservation]:
        latest_by_metric: dict[str, MetricObservation] = {}
        for record in observations:
            current = latest_by_metric.get(record.metric_code)
            if current is None or _observation_sort_key(record) > _observation_sort_key(current):
                latest_by_metric[record.metric_code] = record
        return [latest_by_metric[metric_code] for metric_code in sorted(latest_by_metric)]

    def _plot_feature(self, plot: Plot, observation: MetricObservation | None, metric: Metric | None) -> dict:
        return {
            "type": "Feature",
            "geometry": plot.geometry,
            "properties": {
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
            },
        }

    def _snapshot_from_observation(self, record: MetricObservation) -> PlotMetricSnapshot:
        metric = get_metric_by_code(record.metric_code)
        return PlotMetricSnapshot(
            metric_code=record.metric_code,
            metric_name=metric.metric_name if metric else record.metric_code,
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

    def _quality_counts(self) -> dict[str, int]:
        rows = self.session.execute(
            select(MetricObservationModel.quality_flag, func.count()).group_by(MetricObservationModel.quality_flag)
        ).all()
        counts = {flag: 0 for flag in QUALITY_FLAG_ORDER}
        counts.update({flag: count for flag, count in rows})
        return counts

    def _region_status(self) -> list[RegionStatus]:
        rows = self.session.execute(
            select(PlotModel.region, func.count()).group_by(PlotModel.region).order_by(PlotModel.region)
        ).all()
        result = []
        for region, plot_count in rows:
            warning_count = self.session.scalar(
                select(func.count())
                .select_from(MetricObservationModel)
                .join(PlotModel, MetricObservationModel.plot_id == PlotModel.plot_id)
                .where(
                    PlotModel.region == region,
                    MetricObservationModel.quality_flag.in_(["missing", "outlier", "error"]),
                )
            ) or 0
            result.append(RegionStatus(region=region or "未分区", plot_count=plot_count, warning_count=warning_count))
        return result


def _metric_schema(row: MetricModel) -> Metric:
    source_type = row.source_type if row.source_type in {"simulated", "generated_boundary", "manual", "weather", "remote_sensing", "postgis"} else "postgis"
    return Metric(
        metric_code=row.metric_code,
        metric_name=row.metric_name,
        category=row.category,
        unit=row.unit,
        value_type=row.value_type,
        precision=row.precision,
        normal_range=NormalRange(min=row.normal_min, max=row.normal_max),
        color_scale=row.color_scale,
        description=row.description,
        source_type=source_type,
    )


def _plot_schema(row: PlotModel, *, geometry_json: str | None = None) -> Plot:
    geometry = json.loads(geometry_json) if geometry_json else None
    aliases = [alias.alias for alias in sorted(row.aliases, key=lambda item: item.alias)]
    return Plot(
        plot_id=row.plot_id,
        plot_code=row.plot_code,
        aliases=aliases,
        plot_name=row.plot_name,
        region=row.region,
        geometry=geometry,
        status=row.status,
    )


def _observation_schema(row: MetricObservationModel) -> MetricObservation:
    return MetricObservation(
        id=row.id,
        plot_id=row.plot_id,
        plot_code=row.plot_code,
        metric_code=row.metric_code,
        value=row.value,
        unit=row.unit,
        observed_at=row.observed_at,
        batch_id=row.import_batch_id,
        data_source_id=f"source-{row.import_batch_id}",
        quality_flag=row.quality_flag,
    )


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
