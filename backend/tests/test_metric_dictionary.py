from app.core.metric_dictionary import METRIC_DICTIONARY, get_metric_codes
from app.schemas.data_model import MetricObservation, TwinScenario


EXPECTED_METRIC_CODES = {
    "crop_growth",
    "maturity_prediction",
    "chlorophyll",
    "nitrogen",
    "phosphorus",
    "potassium",
    "ph",
    "organic_matter",
    "soluble_total_salt",
    "leaf_area_index",
    "plant_height",
}

REQUIRED_METRIC_FIELDS = {
    "metric_code",
    "metric_name",
    "category",
    "unit",
    "value_type",
    "precision",
    "normal_range",
    "color_scale",
    "description",
    "source_type",
}

REQUIRED_OBSERVATION_FIELDS = {
    "id",
    "plot_id",
    "plot_code",
    "metric_code",
    "value",
    "unit",
    "observed_at",
    "batch_id",
    "data_source_id",
    "quality_flag",
}

REQUIRED_SCENARIO_FIELDS = {
    "scenario_id",
    "scenario_name",
    "description",
    "data_mode",
    "plot_count",
    "metric_count",
    "date_range",
    "created_at",
}


def test_metric_dictionary_contains_first_version_metrics():
    assert set(get_metric_codes()) == EXPECTED_METRIC_CODES


def test_each_metric_has_required_dictionary_fields():
    for metric in METRIC_DICTIONARY:
        metric_data = metric.model_dump()
        assert REQUIRED_METRIC_FIELDS <= metric_data.keys()
        assert metric.normal_range.min is not None
        assert metric.normal_range.max is not None


def test_metric_observation_schema_keeps_long_table_traceability_fields():
    assert REQUIRED_OBSERVATION_FIELDS <= MetricObservation.model_fields.keys()


def test_twin_scenario_schema_matches_demo_entry_contract():
    assert REQUIRED_SCENARIO_FIELDS <= TwinScenario.model_fields.keys()
