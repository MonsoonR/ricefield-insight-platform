from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ValueType = Literal["float", "int"]
SourceType = Literal["excel", "geojson", "manual"]
QualityFlag = Literal["normal", "missing", "outlier", "error"]
ImportStatus = Literal["pending", "processing", "success", "failed", "partial_success", "partial"]
QualityReportStatus = Literal["success", "partial", "failed"]
IssueSeverity = Literal["info", "warning", "error"]


class NormalRange(BaseModel):
    min: float
    max: float


class Metric(BaseModel):
    metric_code: str
    metric_name: str
    category: str
    unit: str
    value_type: ValueType
    precision: int
    normal_range: NormalRange
    color_scale: str
    description: str
    source_type: SourceType


class Plot(BaseModel):
    plot_id: str
    plot_code: str
    plot_name: str | None = None
    region: str | None = None
    geometry: dict[str, Any] | None = None
    status: str = "normal"


class MetricObservation(BaseModel):
    id: str
    plot_id: str
    plot_code: str
    metric_code: str
    value: float | int | None
    unit: str
    observed_at: date
    import_batch_id: str
    source_file: str
    raw_sheet: str | None = None
    raw_cell: str | None = None
    quality_flag: QualityFlag = "normal"


class ImportBatch(BaseModel):
    import_batch_id: str
    source_file: str
    imported_at: datetime
    status: ImportStatus
    record_count: int = 0
    warning_count: int = 0
    error_count: int = 0


class ImportIssue(BaseModel):
    issue_id: str
    import_batch_id: str
    issue_type: str
    severity: IssueSeverity
    message: str
    source_file: str
    raw_sheet: str | None = None
    raw_cell: str | None = None
    plot_code: str | None = None
    metric_code: str | None = None


class ImportQualityReport(BaseModel):
    import_batch_id: str
    source_file: str
    successful_record_count: int
    missing_value_count: int
    outlier_count: int
    unmatched_plots: list[str]
    error_cells: list[str]
    skipped_record_count: int
    parse_duration_ms: int
    status: QualityReportStatus
    parse_errors: list[str] = Field(default_factory=list)
