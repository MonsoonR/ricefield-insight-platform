from datetime import date

from app.services.importer.excel import parse_excel_directory, parse_excel_file
from tests.fixtures.excel_fixtures import (
    create_observation_workbook,
    create_source_export_workbook,
)


PLOT_LOOKUP = {
    "P001": "plot-001",
    "P002": "plot-002",
}


def test_excel_importer_converts_metric_columns_to_traceable_long_table(tmp_path):
    workbook_path = create_observation_workbook(tmp_path / "sample_observations.xlsx")

    result = parse_excel_file(
        workbook_path,
        plot_lookup=PLOT_LOOKUP,
        import_batch_id="batch-20260506-001",
    )

    assert len(result.records) == 6
    first = result.records[0]
    assert first.plot_id == "plot-001"
    assert first.plot_code == "P001"
    assert first.metric_code == "crop_growth"
    assert first.value == 0.82
    assert first.unit == "score"
    assert first.observed_at == date(2026, 5, 1)
    assert first.import_batch_id == "batch-20260506-001"
    assert first.source_file == "sample_observations.xlsx"
    assert first.raw_sheet == "growth"
    assert first.raw_cell == "C2"
    assert first.quality_flag == "normal"

    records_by_cell = {record.raw_cell: record for record in result.records}
    assert records_by_cell["C3"].quality_flag == "missing"
    assert records_by_cell["C3"].value is None
    assert records_by_cell["D3"].quality_flag == "outlier"
    assert records_by_cell["C6"].quality_flag == "error"
    assert records_by_cell["C6"].value is None


def test_excel_importer_generates_quality_report_without_silent_drops(tmp_path):
    workbook_path = create_observation_workbook(tmp_path / "sample_observations.xlsx")

    result = parse_excel_file(
        workbook_path,
        plot_lookup=PLOT_LOOKUP,
        import_batch_id="batch-20260506-001",
    )

    report = result.report
    assert report.import_batch_id == "batch-20260506-001"
    assert report.source_file == "sample_observations.xlsx"
    assert report.successful_record_count == 3
    assert report.missing_value_count == 1
    assert report.outlier_count == 1
    assert report.unmatched_plots == ["P999"]
    assert report.error_cells == ["B5", "C6"]
    assert report.skipped_record_count == 4
    assert report.parse_duration_ms >= 0
    assert report.status == "partial"


def test_excel_directory_import_reads_all_xlsx_files_from_import_directory(tmp_path):
    imports_dir = tmp_path / "data" / "imports"
    imports_dir.mkdir(parents=True)
    create_observation_workbook(imports_dir / "sample_observations.xlsx")
    (imports_dir / "notes.txt").write_text("not an excel file", encoding="utf-8")

    results = parse_excel_directory(
        imports_dir,
        plot_lookup=PLOT_LOOKUP,
        import_batch_id="batch-20260506-001",
    )

    assert len(results) == 1
    assert results[0].report.source_file == "sample_observations.xlsx"


def test_excel_importer_supports_source_export_cells_with_plot_value_pairs(tmp_path):
    workbook_path = create_source_export_workbook(tmp_path / "source_export.xlsx")

    result = parse_excel_file(
        workbook_path,
        plot_lookup=PLOT_LOOKUP,
        import_batch_id="batch-20260506-002",
    )

    assert len(result.records) == 2
    records_by_cell = {record.raw_cell: record for record in result.records}
    assert records_by_cell["D2"].plot_code == "P001"
    assert records_by_cell["D2"].metric_code == "crop_growth"
    assert records_by_cell["D2"].value == 0.82
    assert records_by_cell["D2"].quality_flag == "normal"
    assert records_by_cell["E2"].plot_code == "P002"
    assert records_by_cell["E2"].quality_flag == "outlier"

    assert result.report.unmatched_plots == ["P999"]
    assert result.report.error_cells == ["G2"]
    assert result.report.skipped_record_count == 2
    assert result.report.status == "partial"
