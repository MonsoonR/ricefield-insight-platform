from app.core.metric_dictionary import METRIC_DICTIONARY, get_metric_codes
from app.schemas.data_model import MetricObservation


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
    "import_batch_id",
    "source_file",
    "raw_sheet",
    "raw_cell",
    "quality_flag",
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
