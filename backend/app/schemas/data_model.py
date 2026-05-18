from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ValueType = Literal["float", "int"]
SourceType = Literal[
    "simulated",
    "generated_boundary",
    "manual",
    "weather",
    "remote_sensing",
    "postgis",
]
DataMode = Literal["demo", "manual", "sensor", "remote_sensing", "postgis"]
QualityFlag = Literal["normal", "missing", "outlier", "error"]
BatchStatus = Literal["pending", "processing", "success", "failed", "partial"]
IssueSeverity = Literal["info", "warning", "error"]
BatchType = Literal["simulated", "manual", "adapter"]


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


class ScenarioDateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class TwinScenario(BaseModel):
    scenario_id: str
    scenario_name: str
    description: str
    data_mode: DataMode
    plot_count: int
    metric_count: int
    date_range: ScenarioDateRange
    created_at: datetime


class Plot(BaseModel):
    plot_id: str
    plot_code: str
    aliases: list[str] = Field(default_factory=list)
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
    batch_id: str
    data_source_id: str
    quality_flag: QualityFlag = "normal"


class ObservationBatch(BaseModel):
    batch_id: str
    scenario_id: str
    data_source_id: str
    batch_name: str
    batch_type: BatchType
    generated_at: datetime
    status: BatchStatus
    record_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    description: str | None = None


class DataSource(BaseModel):
    data_source_id: str
    source_name: str
    source_type: SourceType
    description: str | None = None
    generation_rule: str | None = None
    created_at: datetime


class DataQualityIssue(BaseModel):
    issue_id: str
    scenario_id: str
    batch_id: str | None = None
    data_source_id: str | None = None
    issue_type: QualityFlag
    severity: IssueSeverity
    message: str
    plot_id: str | None = None
    plot_code: str | None = None
    metric_code: str | None = None
    observed_at: date | None = None
    value: float | int | None = None
