from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import sin

from app.core.metric_dictionary import METRIC_DICTIONARY, get_metric_by_code
from app.schemas.data_model import (
    DataQualityIssue,
    DataSource,
    MetricObservation,
    ObservationBatch,
    Plot,
)
from app.schemas.mvp_api import ScenarioDateRange, TwinScenario


DEMO_SCENARIO_ID = "demo-ricefield-2025"
DEMO_BATCH_ID = "batch-demo-ricefield-2025"
DEMO_DATA_SOURCE_ID = "source-demo-ricefield-simulated"
DEMO_BOUNDARY_SOURCE_ID = "source-demo-ricefield-boundary"
DEMO_START_DATE = date(2025, 6, 1)
DEMO_DAY_COUNT = 45
DEMO_CREATED_AT = datetime(2025, 7, 15, 9, 0, 0)


@dataclass(frozen=True)
class DemoDataBundle:
    scenario: TwinScenario
    plots: list[Plot]
    observations: list[MetricObservation]
    observation_batch: ObservationBatch
    data_sources: list[DataSource]
    quality_issues: list[DataQualityIssue]


def build_demo_data_bundle() -> DemoDataBundle:
    dates = [DEMO_START_DATE + timedelta(days=offset) for offset in range(DEMO_DAY_COUNT)]
    scenario = TwinScenario(
        scenario_id=DEMO_SCENARIO_ID,
        scenario_name="稻田数字孪生演示场景 2025",
        description="面向大创答辩的自建模拟场景，包含两片试验区、程序生成地块边界和多指标时序观测。",
        data_mode="demo",
        plot_count=8,
        metric_count=len(METRIC_DICTIONARY),
        date_range=ScenarioDateRange(start_date=dates[0], end_date=dates[-1]),
        created_at=DEMO_CREATED_AT,
    )
    plots = _build_demo_plots()
    observations = _build_demo_observations(plots, dates)
    quality_issues = _build_quality_issues(observations, plots)
    observation_batch = ObservationBatch(
        batch_id=DEMO_BATCH_ID,
        scenario_id=DEMO_SCENARIO_ID,
        data_source_id=DEMO_DATA_SOURCE_ID,
        batch_name="稻田数字孪生模拟观测批次",
        batch_type="simulated",
        generated_at=DEMO_CREATED_AT,
        status="partial" if quality_issues else "success",
        record_count=len(observations),
        warning_count=len(quality_issues),
        error_count=sum(1 for item in quality_issues if item.severity == "error"),
        description="程序生成的多指标时序数据，内置少量缺失和异常点用于演示预警。",
    )
    data_sources = [
        DataSource(
            data_source_id=DEMO_BOUNDARY_SOURCE_ID,
            source_name="程序生成示例地块边界",
            source_type="generated_boundary",
            description="按固定经纬度规则生成两片试验区共 8 个示例地块。",
            generation_rule="2 个区域 x 4 个矩形地块，WGS84 坐标。",
            created_at=DEMO_CREATED_AT,
        ),
        DataSource(
            data_source_id=DEMO_DATA_SOURCE_ID,
            source_name="模拟多指标观测数据",
            source_type="simulated",
            description="按作物生长进程、区域差异和少量扰动生成时序指标。",
            generation_rule="45 天 x 8 地块 x 11 指标，注入 2 个缺失点和 4 个异常点。",
            created_at=DEMO_CREATED_AT,
        ),
    ]
    return DemoDataBundle(
        scenario=scenario,
        plots=plots,
        observations=observations,
        observation_batch=observation_batch,
        data_sources=data_sources,
        quality_issues=quality_issues,
    )


def _build_demo_plots() -> list[Plot]:
    zone1_origin = (125.310, 43.870)
    zone2_origin = (125.326, 43.870)
    plots: list[Plot] = []
    for index in range(4):
        plots.append(
            _demo_plot(
                plot_id=f"{DEMO_SCENARIO_ID}-A{index + 1:02d}",
                plot_code=f"A{index + 1:02d}",
                plot_name=f"试验一区-A{index + 1:02d}",
                region="试验一区",
                origin=zone1_origin,
                index=index,
            )
        )
        plots.append(
            _demo_plot(
                plot_id=f"{DEMO_SCENARIO_ID}-B{index + 1:02d}",
                plot_code=f"B{index + 1:02d}",
                plot_name=f"试验二区-B{index + 1:02d}",
                region="试验二区",
                origin=zone2_origin,
                index=index,
            )
        )
    return plots


def _demo_plot(
    *,
    plot_id: str,
    plot_code: str,
    plot_name: str,
    region: str,
    origin: tuple[float, float],
    index: int,
) -> Plot:
    col = index % 2
    row = index // 2
    lon = origin[0] + col * 0.0048
    lat = origin[1] + row * 0.0038
    width = 0.0036
    height = 0.0026
    return Plot(
        plot_id=plot_id,
        plot_code=plot_code,
        aliases=[plot_code, plot_name],
        plot_name=plot_name,
        region=region,
        geometry={
            "type": "Polygon",
            "coordinates": [
                [
                    [lon, lat],
                    [lon + width, lat],
                    [lon + width, lat + height],
                    [lon, lat + height],
                    [lon, lat],
                ]
            ],
        },
        status="normal",
    )


def _build_demo_observations(
    plots: list[Plot],
    dates: list[date],
) -> list[MetricObservation]:
    observations: list[MetricObservation] = []
    plot_count = max(len(plots), 1)
    day_count = max(len(dates) - 1, 1)
    for plot_index, plot in enumerate(plots):
        plot_factor = (plot_index + 1) / plot_count
        for day_index, observed_at in enumerate(dates):
            progress = day_index / day_count
            for metric in METRIC_DICTIONARY:
                value = _metric_value(metric.metric_code, progress, plot_factor, day_index)
                quality_flag = "normal"
                anomaly = _demo_anomaly(plot.plot_code, metric.metric_code, observed_at, dates[-1])
                if anomaly == "missing":
                    value = None
                    quality_flag = "missing"
                elif anomaly == "outlier":
                    value = _outlier_value(metric.metric_code)
                    quality_flag = "outlier"

                observations.append(
                    MetricObservation(
                        id=f"{DEMO_SCENARIO_ID}-{plot.plot_code}-{metric.metric_code}-{observed_at.isoformat()}",
                        plot_id=plot.plot_id,
                        plot_code=plot.plot_code,
                        metric_code=metric.metric_code,
                        value=value,
                        unit=metric.unit,
                        observed_at=observed_at,
                        batch_id=DEMO_BATCH_ID,
                        data_source_id=DEMO_DATA_SOURCE_ID,
                        quality_flag=quality_flag,
                    )
                )
    return observations


def _build_quality_issues(
    observations: list[MetricObservation],
    plots: list[Plot],
) -> list[DataQualityIssue]:
    plots_by_id = {plot.plot_id: plot for plot in plots}
    issues: list[DataQualityIssue] = []
    for record in observations:
        if record.quality_flag == "normal":
            continue
        plot = plots_by_id[record.plot_id]
        metric = get_metric_by_code(record.metric_code)
        metric_name = metric.metric_name if metric else record.metric_code
        issue_type = record.quality_flag
        issues.append(
            DataQualityIssue(
                issue_id=f"warning-{record.id}",
                scenario_id=DEMO_SCENARIO_ID,
                batch_id=record.batch_id,
                data_source_id=record.data_source_id,
                issue_type=issue_type,
                severity="warning" if issue_type == "missing" else "error",
                message=f"{plot.plot_name} 在 {record.observed_at.isoformat()} 的{metric_name}出现{'缺失' if issue_type == 'missing' else '异常'}。",
                plot_id=record.plot_id,
                plot_code=record.plot_code,
                metric_code=record.metric_code,
                observed_at=record.observed_at,
                value=record.value,
            )
        )
    return issues


def _metric_value(metric_code: str, progress: float, plot_factor: float, day_index: int) -> float | int:
    wave = sin(day_index / 5 + plot_factor * 3)
    if metric_code == "crop_growth":
        return round(0.62 + progress * 0.28 + plot_factor * 0.05 + wave * 0.015, 2)
    if metric_code == "maturity_prediction":
        return int(round(126 - progress * 34 + plot_factor * 5))
    if metric_code == "chlorophyll":
        return round(34 + progress * 8 + plot_factor * 3 + wave * 1.2, 2)
    if metric_code == "nitrogen":
        return round(118 + plot_factor * 28 - progress * 10 + wave * 4, 2)
    if metric_code == "phosphorus":
        return round(18 + plot_factor * 8 - progress * 1.5 + wave * 1.1, 2)
    if metric_code == "potassium":
        return round(112 + plot_factor * 36 - progress * 8 + wave * 5, 2)
    if metric_code == "ph":
        return round(6.2 + plot_factor * 0.35 + wave * 0.08, 2)
    if metric_code == "organic_matter":
        return round(25 + plot_factor * 5 - progress * 0.8 + wave * 0.5, 2)
    if metric_code == "soluble_total_salt":
        return round(0.42 + plot_factor * 0.3 + wave * 0.04, 3)
    if metric_code == "leaf_area_index":
        return round(3.2 + progress * 2.5 + plot_factor * 0.45 + wave * 0.12, 2)
    if metric_code == "plant_height":
        return round(62 + progress * 42 + plot_factor * 7 + wave * 1.8, 1)
    return round(progress + plot_factor, 2)


def _demo_anomaly(
    plot_code: str,
    metric_code: str,
    observed_at: date,
    latest_date: date,
) -> str | None:
    anomaly_dates = {
        ("A03", "crop_growth", latest_date): "missing",
        ("B04", "crop_growth", latest_date): "outlier",
        ("A01", "leaf_area_index", date(2025, 6, 20)): "missing",
        ("B02", "chlorophyll", date(2025, 7, 3)): "outlier",
        ("A02", "ph", date(2025, 6, 18)): "outlier",
        ("B03", "plant_height", date(2025, 6, 25)): "outlier",
    }
    return anomaly_dates.get((plot_code, metric_code, observed_at))


def _outlier_value(metric_code: str) -> float | int:
    values: dict[str, float | int] = {
        "crop_growth": 1.22,
        "chlorophyll": 64.0,
        "ph": 8.6,
        "plant_height": 155.0,
    }
    return values.get(metric_code, 999.0)
