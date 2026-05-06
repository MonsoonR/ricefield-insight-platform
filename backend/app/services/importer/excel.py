from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import pandas as pd
from openpyxl.utils import get_column_letter

from app.core.metric_dictionary import get_metric_by_code, get_metric_codes
from app.schemas.data_model import ImportQualityReport, MetricObservation


REQUIRED_COLUMNS = {"plot_code", "observed_at"}
SOURCE_EXPORT_COLUMNS = {"type", "地块", "时间"}
SOURCE_EXPORT_DATA_START_INDEX = 3
METRIC_TYPE_CODE_MAP = {
    "11": "crop_growth",
    "16": "maturity_prediction",
    "43": "chlorophyll",
    "131": "nitrogen",
    "132": "phosphorus",
    "133": "potassium",
    "134": "ph",
    "135": "organic_matter",
    "136": "soluble_total_salt",
    "434": "leaf_area_index",
    "435": "plant_height",
}


@dataclass(frozen=True)
class ExcelImportResult:
    records: list[MetricObservation]
    report: ImportQualityReport


def parse_excel_directory(
    imports_dir: str | Path,
    *,
    plot_lookup: dict[str, str],
    import_batch_id: str,
) -> list[ExcelImportResult]:
    directory = Path(imports_dir)
    return [
        parse_excel_file(
            excel_file,
            plot_lookup=plot_lookup,
            import_batch_id=import_batch_id,
        )
        for excel_file in sorted(directory.glob("*.xlsx"))
        if not excel_file.name.startswith("~$")
    ]


def parse_excel_file(
    file_path: str | Path,
    *,
    plot_lookup: dict[str, str],
    import_batch_id: str,
) -> ExcelImportResult:
    source_path = Path(file_path)
    started_at = perf_counter()
    records: list[MetricObservation] = []
    missing_value_count = 0
    outlier_count = 0
    skipped_record_count = 0
    unmatched_plots: set[str] = set()
    error_cells: list[str] = []
    parse_errors: list[str] = []

    try:
        workbook = pd.read_excel(source_path, sheet_name=None, engine="openpyxl")
    except Exception as exc:
        duration_ms = _duration_ms(started_at)
        report = ImportQualityReport(
            import_batch_id=import_batch_id,
            source_file=source_path.name,
            successful_record_count=0,
            missing_value_count=0,
            outlier_count=0,
            unmatched_plots=[],
            error_cells=[],
            skipped_record_count=0,
            parse_duration_ms=duration_ms,
            status="failed",
            parse_errors=[f"无法读取 Excel 文件：{exc}"],
        )
        return ExcelImportResult(records=[], report=report)

    known_metric_codes = set(get_metric_codes())

    for sheet_name, dataframe in workbook.items():
        if dataframe.empty:
            continue

        normalized_columns = [str(column).strip() for column in dataframe.columns]
        dataframe = dataframe.copy()
        dataframe.columns = normalized_columns

        column_positions = {
            column: index + 1 for index, column in enumerate(normalized_columns)
        }

        if SOURCE_EXPORT_COLUMNS <= set(normalized_columns):
            for row_index, row in dataframe.iterrows():
                excel_row_number = int(row_index) + 2
                metric_code = _metric_code_from_source_type(row["type"])
                data_cell_count = _count_source_data_cells(row)

                if metric_code is None:
                    skipped_record_count += data_cell_count
                    error_cells.append(_cell_ref(column_positions["type"], excel_row_number))
                    continue

                metric = get_metric_by_code(metric_code)
                if metric is None:
                    skipped_record_count += data_cell_count
                    error_cells.append(_cell_ref(column_positions["type"], excel_row_number))
                    continue

                observed_at = _parse_observed_at(row["时间"])
                if observed_at is None:
                    skipped_record_count += data_cell_count
                    error_cells.append(_cell_ref(column_positions["时间"], excel_row_number))
                    continue

                for column_index in range(
                    SOURCE_EXPORT_DATA_START_INDEX,
                    len(normalized_columns),
                ):
                    raw_cell_value = row.iloc[column_index]
                    if pd.isna(raw_cell_value):
                        continue

                    raw_cell = _cell_ref(column_index + 1, excel_row_number)
                    parsed_pair = _parse_source_plot_value(raw_cell_value)
                    if parsed_pair is None:
                        skipped_record_count += 1
                        error_cells.append(raw_cell)
                        continue

                    plot_code, metric_raw_value = parsed_pair
                    plot_id = plot_lookup.get(plot_code)
                    if plot_id is None:
                        skipped_record_count += 1
                        unmatched_plots.add(plot_code)
                        continue

                    quality_flag = "normal"
                    value: float | int | None
                    if metric_raw_value == "":
                        value = None
                        quality_flag = "missing"
                        missing_value_count += 1
                    else:
                        value = _coerce_metric_value(
                            metric_raw_value,
                            metric.value_type,
                            metric.precision,
                        )
                        if value is None:
                            quality_flag = "error"
                            error_cells.append(raw_cell)
                        elif (
                            value < metric.normal_range.min
                            or value > metric.normal_range.max
                        ):
                            quality_flag = "outlier"
                            outlier_count += 1

                    record_key = (
                        f"{import_batch_id}:{source_path.name}:{sheet_name}:"
                        f"{raw_cell}:{plot_code}:{metric_code}"
                    )
                    records.append(
                        MetricObservation(
                            id=str(uuid5(NAMESPACE_URL, record_key)),
                            plot_id=plot_id,
                            plot_code=plot_code,
                            metric_code=metric_code,
                            value=value,
                            unit=metric.unit,
                            observed_at=observed_at,
                            import_batch_id=import_batch_id,
                            source_file=source_path.name,
                            raw_sheet=sheet_name,
                            raw_cell=raw_cell,
                            quality_flag=quality_flag,
                        )
                    )

            continue

        missing_columns = REQUIRED_COLUMNS - set(normalized_columns)
        metric_columns = [column for column in normalized_columns if column in known_metric_codes]

        if missing_columns:
            parse_errors.append(
                f"工作表 {sheet_name} 缺少必填列：{', '.join(sorted(missing_columns))}"
            )
            continue

        if not metric_columns:
            parse_errors.append(f"工作表 {sheet_name} 未找到指标字典中的指标列")
            continue

        for row_index, row in dataframe.iterrows():
            excel_row_number = int(row_index) + 2
            metric_cell_count = len(metric_columns)
            plot_code = _clean_text(row["plot_code"])

            if not plot_code:
                skipped_record_count += metric_cell_count
                error_cells.append(_cell_ref(column_positions["plot_code"], excel_row_number))
                continue

            plot_id = plot_lookup.get(plot_code)
            if plot_id is None:
                skipped_record_count += metric_cell_count
                unmatched_plots.add(plot_code)
                continue

            observed_at = _parse_observed_at(row["observed_at"])
            if observed_at is None:
                skipped_record_count += metric_cell_count
                error_cells.append(
                    _cell_ref(column_positions["observed_at"], excel_row_number)
                )
                continue

            for metric_code in metric_columns:
                metric = get_metric_by_code(metric_code)
                if metric is None:
                    skipped_record_count += 1
                    continue

                raw_cell = _cell_ref(column_positions[metric_code], excel_row_number)
                raw_value = row[metric_code]
                quality_flag = "normal"
                value: float | int | None

                if pd.isna(raw_value):
                    value = None
                    quality_flag = "missing"
                    missing_value_count += 1
                else:
                    value = _coerce_metric_value(raw_value, metric.value_type, metric.precision)
                    if value is None:
                        quality_flag = "error"
                        error_cells.append(raw_cell)
                    elif (
                        value < metric.normal_range.min
                        or value > metric.normal_range.max
                    ):
                        quality_flag = "outlier"
                        outlier_count += 1

                record_key = (
                    f"{import_batch_id}:{source_path.name}:{sheet_name}:"
                    f"{raw_cell}:{plot_code}:{metric_code}"
                )
                records.append(
                    MetricObservation(
                        id=str(uuid5(NAMESPACE_URL, record_key)),
                        plot_id=plot_id,
                        plot_code=plot_code,
                        metric_code=metric_code,
                        value=value,
                        unit=metric.unit,
                        observed_at=observed_at,
                        import_batch_id=import_batch_id,
                        source_file=source_path.name,
                        raw_sheet=sheet_name,
                        raw_cell=raw_cell,
                        quality_flag=quality_flag,
                    )
                )

    successful_record_count = sum(
        1 for record in records if record.quality_flag == "normal"
    )
    has_issue = any(
        [
            missing_value_count,
            outlier_count,
            unmatched_plots,
            error_cells,
            skipped_record_count,
            parse_errors,
        ]
    )
    status = "failed" if not records else "partial" if has_issue else "success"

    report = ImportQualityReport(
        import_batch_id=import_batch_id,
        source_file=source_path.name,
        successful_record_count=successful_record_count,
        missing_value_count=missing_value_count,
        outlier_count=outlier_count,
        unmatched_plots=sorted(unmatched_plots),
        error_cells=sorted(set(error_cells), key=error_cells.index),
        skipped_record_count=skipped_record_count,
        parse_duration_ms=_duration_ms(started_at),
        status=status,
        parse_errors=parse_errors,
    )
    return ExcelImportResult(records=records, report=report)


def _clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _parse_observed_at(value: object) -> date | None:
    if pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _coerce_metric_value(
    value: object,
    value_type: str,
    precision: int,
) -> float | int | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if value_type == "int":
        if not number.is_integer():
            return None
        return int(number)

    return round(number, precision)


def _metric_code_from_source_type(value: object) -> str | None:
    type_code = _clean_text(value)
    if type_code.endswith(".0"):
        type_code = type_code[:-2]
    return METRIC_TYPE_CODE_MAP.get(type_code)


def _parse_source_plot_value(value: object) -> tuple[str, str] | None:
    text = _clean_text(value)
    if ":" not in text:
        return None

    plot_part, value_part = text.split(":", 1)
    plot_code = _strip_source_token(plot_part)
    metric_value = _strip_source_token(value_part)

    if not plot_code:
        return None

    return plot_code, metric_value


def _strip_source_token(value: str) -> str:
    return value.strip().strip("{}").strip().strip('"').strip("'").strip("“”").strip()


def _count_source_data_cells(row: Any) -> int:
    count = 0
    for value in row.iloc[SOURCE_EXPORT_DATA_START_INDEX:]:
        if not pd.isna(value):
            count += 1
    return count


def _cell_ref(column_index: int, row_number: int) -> str:
    return f"{get_column_letter(column_index)}{row_number}"


def _duration_ms(started_at: float) -> int:
    return max(0, int((perf_counter() - started_at) * 1000))
