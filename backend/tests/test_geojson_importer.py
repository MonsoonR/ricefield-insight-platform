from pathlib import Path

from app.services.importer.geojson import (
    build_plot_lookup,
    normalize_plot_code,
    parse_geojson_directory,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "geojson"


def test_normalize_plot_code_handles_case_spacing_suffix_and_region():
    assert normalize_plot_code(" 21a-1 ") == "21A"
    assert normalize_plot_code("21A") == "21A"
    assert normalize_plot_code("E1-16", region="东区") == "E1-16"


def test_parse_geojson_directory_outputs_plots_aliases_and_match_report():
    result = parse_geojson_directory(
        FIXTURE_DIR,
        excel_plot_codes=["21A", "64C", "P999"],
    )

    plots_by_id = {plot.plot_id: plot for plot in result.plots}
    east_21a = plots_by_id["east-21A"]
    west_21a = plots_by_id["west-21A"]
    assert east_21a.plot_code == "21A"
    assert east_21a.region == "东区"
    assert west_21a.region == "西区"
    assert east_21a.geometry["type"] == "Polygon"

    assert result.plot_aliases["21A"] == ["east-21A", "west-21A"]
    assert result.plot_aliases["64C"] == ["east-64A"]
    assert result.report.duplicate_plot_codes == ["东区:S15"]
    assert result.report.garbled_plot_codes == ["锛�乱码"]
    assert result.report.unmatched_excel_plots == ["P999"]
    assert result.report.geojson_plots_without_excel_data == [
        "东区:24-1C",
        "东区:S15",
        "西区:21A",
    ]
    assert plots_by_id["east-S15"].status == "duplicate"
    assert plots_by_id["east-64A"].status == "normal"


def test_build_plot_lookup_maps_many_aliases_to_one_plot_id():
    result = parse_geojson_directory(FIXTURE_DIR)

    lookup = build_plot_lookup(result.plots)
    assert {key: lookup[key] for key in ("24-1A", "24-1C", "64A", "64C")} == {
        "24-1A": "east-24-1C",
        "24-1C": "east-24-1C",
        "64A": "east-64A",
        "64C": "east-64A",
    }
