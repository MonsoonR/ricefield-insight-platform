from __future__ import annotations

from collections.abc import Generator
from typing import Annotated
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.metric_dictionary import get_metric_by_code
from app.db.session import get_data_backend, get_session_factory
from app.schemas.mvp_api import (
    AnalysisQuery,
    CorrelationResponse,
    DatesQuery,
    DatesResponse,
    MapLayersQuery,
    MapLayersResponse,
    MetricCompareResponse,
    MetricsResponse,
    PlotListQuery,
    PlotSeriesQuery,
    PlotSeriesResponse,
    PlotSummaryResponse,
    PlotsResponse,
    ScenarioQuery,
    ScenarioOverviewResponse,
    ScenariosResponse,
    TwinScenario,
    WarningsResponse,
)
from app.services.database_data import DatabaseDataStore
from app.services.mvp_data import get_default_store


router = APIRouter(tags=["MVP 数据接口"])


def get_mvp_data_store() -> Generator[Any, None, None]:
    if get_data_backend() == "postgres":
        session_factory = get_session_factory()
        with session_factory() as session:
            yield DatabaseDataStore(session)
        return

    yield get_default_store()


@router.get("/scenarios", response_model=ScenariosResponse)
def read_scenarios(
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> ScenariosResponse:
    return data_store.list_scenarios()


@router.get("/scenarios/current", response_model=TwinScenario)
def read_current_scenario(
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> TwinScenario:
    return data_store.get_current_scenario()


@router.get("/scenarios/{scenario_id}", response_model=TwinScenario)
def read_scenario(
    scenario_id: str,
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> TwinScenario:
    scenario = data_store.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"未找到场景：{scenario_id}")
    return scenario


@router.get("/scenarios/{scenario_id}/overview", response_model=ScenarioOverviewResponse)
def read_scenario_overview(
    scenario_id: str,
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> ScenarioOverviewResponse:
    _ensure_scenario_exists(scenario_id, data_store)
    return data_store.get_scenario_overview(scenario_id)


@router.get("/metrics", response_model=MetricsResponse)
def read_metrics(
    query: Annotated[ScenarioQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> MetricsResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    return data_store.list_metrics()


@router.get("/plots", response_model=PlotsResponse)
def read_plots(
    query: Annotated[PlotListQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> PlotsResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    return data_store.list_plots(query)


@router.get("/dates", response_model=DatesResponse)
def read_dates(
    query: Annotated[DatesQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> DatesResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    _ensure_metric_exists(query.metric_code)
    dates = data_store.list_dates(metric_code=query.metric_code, plot_id=query.plot_id)
    return DatesResponse(items=dates, total=len(dates))


@router.get("/map/layers", response_model=MapLayersResponse)
def read_map_layers(
    query: Annotated[MapLayersQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> MapLayersResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    _ensure_metric_exists(query.metric_code)
    return data_store.get_map_layers(query)


@router.get("/plots/{plotId}/summary", response_model=PlotSummaryResponse)
def read_plot_summary(
    plotId: str,
    query: Annotated[ScenarioQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> PlotSummaryResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    summary = data_store.get_plot_summary(plotId)
    if summary is None:
        raise HTTPException(status_code=404, detail=f"未找到地块：{plotId}")
    return summary


@router.get("/plots/{plotId}/series", response_model=PlotSeriesResponse)
def read_plot_series(
    plotId: str,
    query: Annotated[PlotSeriesQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> PlotSeriesResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    _ensure_metric_exists(query.metric_code)
    series = data_store.get_plot_series(plotId, query)
    if series is None:
        raise HTTPException(status_code=404, detail=f"未找到地块：{plotId}")
    return series


@router.get("/analysis/correlation", response_model=CorrelationResponse)
def read_correlation(
    query: Annotated[AnalysisQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> CorrelationResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    _ensure_metric_exists(query.metric_code)
    return data_store.get_correlation_placeholder(query)


@router.get("/analysis/metric-compare", response_model=MetricCompareResponse)
def read_metric_compare(
    query: Annotated[AnalysisQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> MetricCompareResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    _ensure_metric_exists(query.metric_code)
    return data_store.get_metric_compare(query)


@router.get("/analysis/warnings", response_model=WarningsResponse)
def read_warnings(
    query: Annotated[AnalysisQuery, Depends()],
    data_store: Annotated[Any, Depends(get_mvp_data_store)],
) -> WarningsResponse:
    _ensure_scenario_exists(query.scenario_id, data_store)
    _ensure_metric_exists(query.metric_code)
    return data_store.get_warnings(query)


def _ensure_metric_exists(metric_code: str | None) -> None:
    if metric_code is not None and get_metric_by_code(metric_code) is None:
        raise HTTPException(status_code=404, detail=f"未找到指标：{metric_code}")


def _ensure_scenario_exists(scenario_id: str | None, data_store: Any) -> None:
    if scenario_id is not None and data_store.get_scenario(scenario_id) is None:
        raise HTTPException(status_code=404, detail=f"未找到场景：{scenario_id}")
