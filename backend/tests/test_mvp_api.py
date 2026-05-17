from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.mvp import get_mvp_data_store
from app.main import app
from app.schemas.mvp_api import MapLayersQuery, PlotSeriesQuery
from app.services.mvp_data import MvpDataStore


@pytest.fixture()
def demo_store(tmp_path: Path) -> MvpDataStore:
    return MvpDataStore(
        geojson_dir=tmp_path / "geojson",
        observations_dir=tmp_path / "observations",
    )


@pytest.fixture()
def client_with_demo_data(demo_store: MvpDataStore) -> TestClient:
    app.dependency_overrides[get_mvp_data_store] = lambda: demo_store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_scenario_apis_return_default_current_demo_scenario(
    client_with_demo_data: TestClient,
):
    scenarios_response = client_with_demo_data.get("/api/scenarios")
    current_response = client_with_demo_data.get("/api/scenarios/current")
    detail_response = client_with_demo_data.get("/api/scenarios/demo-ricefield-2025")

    assert scenarios_response.status_code == 200
    scenarios = scenarios_response.json()
    assert scenarios["total"] == 1
    assert scenarios["current_scenario_id"] == "demo-ricefield-2025"
    assert scenarios["items"][0]["scenario_id"] == "demo-ricefield-2025"

    assert current_response.status_code == 200
    current = current_response.json()
    assert current["scenario_id"] == "demo-ricefield-2025"
    assert current["data_mode"] == "demo"
    assert current["plot_count"] == 8
    assert current["metric_count"] == 11
    assert current["date_range"] == {
        "start_date": "2025-06-01",
        "end_date": "2025-07-15",
    }

    assert detail_response.status_code == 200
    assert detail_response.json() == current


def test_existing_twin_apis_accept_scenario_id_and_reject_unknown_scenario(
    client_with_demo_data: TestClient,
):
    explicit_metrics = client_with_demo_data.get(
        "/api/metrics?scenario_id=demo-ricefield-2025"
    )
    default_metrics = client_with_demo_data.get("/api/metrics")
    explicit_plots = client_with_demo_data.get(
        "/api/plots?scenario_id=demo-ricefield-2025"
    )
    unknown_scenario = client_with_demo_data.get("/api/plots?scenario_id=not-found")

    assert explicit_metrics.status_code == 200
    assert explicit_metrics.json() == default_metrics.json()

    assert explicit_plots.status_code == 200
    assert explicit_plots.json()["total"] == 8

    assert unknown_scenario.status_code == 404
    assert unknown_scenario.json()["detail"] == "未找到场景：not-found"


def test_local_data_layer_uses_complete_demo_ricefield_scenario(
    demo_store: MvpDataStore,
):
    scenario = demo_store.get_current_scenario()
    snapshot = demo_store.get_snapshot()
    dates = demo_store.list_dates(metric_code="crop_growth")
    layer = demo_store.get_map_layers(
        MapLayersQuery(metric_code="crop_growth", observed_at=dates[-1])
    )
    series = demo_store.get_plot_series(
        "demo-ricefield-2025-A01",
        PlotSeriesQuery(metric_code="crop_growth"),
    )

    assert scenario.scenario_id == "demo-ricefield-2025"
    assert scenario.data_mode == "demo"
    assert scenario.plot_count == 8
    assert {plot.region for plot in snapshot.plots} == {"试验一区", "试验二区"}
    assert {metric.metric_code for metric in snapshot.metrics} >= {
        "crop_growth",
        "chlorophyll",
        "nitrogen",
        "phosphorus",
        "potassium",
        "ph",
        "organic_matter",
        "leaf_area_index",
        "plant_height",
    }
    assert len(dates) == 45
    assert len(snapshot.observations) == 8 * 11 * 45
    assert snapshot.observation_batches[0].batch_id == "batch-demo-ricefield-2025"
    assert snapshot.observation_batches[0].warning_count >= 3

    features = layer.layers[0].feature_collection["features"]
    latest_flags = {feature["properties"]["quality_flag"] for feature in features}
    assert len(features) == 8
    assert {"normal", "missing", "outlier"} <= latest_flags
    assert series is not None
    assert len(series.series[0].points) == 45


def test_scenario_overview_returns_dashboard_ready_twin_state(
    client_with_demo_data: TestClient,
):
    response = client_with_demo_data.get("/api/scenarios/demo-ricefield-2025/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"]["scenario_id"] == "demo-ricefield-2025"
    assert body["stat_cards"] == [
        {"label": "地块数量", "value": "8", "note": "程序生成示例地块"},
        {"label": "指标数量", "value": "11", "note": "数字孪生指标字典"},
        {"label": "观测天数", "value": "45", "note": "2025-06-01 至 2025-07-15"},
        {"label": "预警数量", "value": "6", "note": "缺失、异常和突变提示"},
    ]
    assert body["health_score"] == 92
    assert body["default_metric_code"] == "crop_growth"
    assert body["default_observed_at"] == "2025-07-15"
    assert body["quality_counts"]["missing"] == 2
    assert body["quality_counts"]["outlier"] == 4
    assert body["region_status"] == [
        {"region": "试验一区", "plot_count": 4, "warning_count": 3},
        {"region": "试验二区", "plot_count": 4, "warning_count": 3},
    ]


def test_map_layers_plot_summary_and_series_return_twin_metric_data(
    client_with_demo_data: TestClient,
):
    layer_response = client_with_demo_data.get(
        "/api/map/layers?metric_code=crop_growth&observed_at=2025-07-15"
    )
    summary_response = client_with_demo_data.get(
        "/api/plots/demo-ricefield-2025-A01/summary"
    )
    series_response = client_with_demo_data.get(
        "/api/plots/demo-ricefield-2025-A01/series?metric_code=crop_growth"
    )

    assert layer_response.status_code == 200
    layer_body = layer_response.json()
    feature = layer_body["layers"][0]["feature_collection"]["features"][0]
    assert feature["properties"]["plot_id"] == "demo-ricefield-2025-A01"
    assert feature["properties"]["metric_code"] == "crop_growth"
    assert feature["properties"]["quality_flag"] == "normal"
    assert "batch_id" in feature["properties"]
    assert "source_file" not in feature["properties"]

    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["plot"]["plot_id"] == "demo-ricefield-2025-A01"
    assert summary["batch_ids"] == ["batch-demo-ricefield-2025"]
    assert {item["metric_code"] for item in summary["latest_observations"]} >= {
        "crop_growth",
        "plant_height",
    }
    assert all("source_file" not in item for item in summary["latest_observations"])

    assert series_response.status_code == 200
    series = series_response.json()["series"][0]
    assert series["metric_code"] == "crop_growth"
    assert len(series["points"]) == 45
    assert "batch_id" in series["points"][0]
    assert "source_cell" not in series["points"][0]


def test_metric_compare_returns_ranked_plot_values(client_with_demo_data: TestClient):
    response = client_with_demo_data.get(
        "/api/analysis/metric-compare?metric_code=crop_growth&observed_at=2025-07-15"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["metric_code"] == "crop_growth"
    assert body["observed_at"] == "2025-07-15"
    assert body["total"] == 8
    assert body["items"][0]["rank"] == 1
    assert body["items"][0]["plot_code"]
    assert body["items"][0]["value"] is not None
    assert body["items"] == sorted(body["items"], key=lambda item: item["rank"])


def test_warnings_api_returns_real_demo_quality_events(client_with_demo_data: TestClient):
    response = client_with_demo_data.get("/api/analysis/warnings")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert {item["warning_type"] for item in body["items"]} == {"missing", "outlier"}
    assert body["items"][0]["scenario_id"] == "demo-ricefield-2025"
    assert body["items"][0]["message"]
    assert all("source_file" not in item for item in body["items"])


def test_removed_import_and_export_routes_are_not_part_of_twin_mvp(
    client_with_demo_data: TestClient,
):
    imports_response = client_with_demo_data.get("/api/imports")
    report_response = client_with_demo_data.get("/api/imports/not-found/report")
    export_response = client_with_demo_data.get("/api/export/report")

    assert imports_response.status_code == 404
    assert report_response.status_code == 404
    assert export_response.status_code == 404


def test_missing_resources_return_readable_chinese_errors(
    client_with_demo_data: TestClient,
):
    plot_response = client_with_demo_data.get("/api/plots/not-found/summary")
    warning_response = client_with_demo_data.get(
        "/api/analysis/warnings?scenario_id=not-found"
    )

    assert plot_response.status_code == 404
    assert plot_response.json()["detail"] == "未找到地块：not-found"

    assert warning_response.status_code == 404
    assert warning_response.json()["detail"] == "未找到场景：not-found"
