from __future__ import annotations

from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MetricModel(Base):
    __tablename__ = "metrics"

    metric_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str] = mapped_column(String(64), nullable=False)
    value_type: Mapped[str] = mapped_column(String(16), nullable=False)
    precision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    normal_min: Mapped[float] = mapped_column(Float, nullable=False)
    normal_max: Mapped[float] = mapped_column(Float, nullable=False)
    color_scale: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)

    observations: Mapped[list["MetricObservationModel"]] = relationship(back_populates="metric")


class PlotModel(Base):
    __tablename__ = "plots"

    plot_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    plot_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    plot_name: Mapped[str | None] = mapped_column(String(255))
    region: Mapped[str | None] = mapped_column(String(64), index=True)
    geometry: Mapped[object | None] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="normal", index=True)

    aliases: Mapped[list["PlotAliasModel"]] = relationship(
        back_populates="plot",
        cascade="all, delete-orphan",
    )
    observations: Mapped[list["MetricObservationModel"]] = relationship(back_populates="plot")


class PlotAliasModel(Base):
    __tablename__ = "plot_aliases"
    __table_args__ = (
        UniqueConstraint("alias", "plot_id", name="uq_plot_aliases_alias_plot_id"),
        Index("ix_plot_aliases_alias", "alias"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.plot_id", ondelete="CASCADE"), nullable=False)
    alias: Mapped[str] = mapped_column(String(128), nullable=False)

    plot: Mapped[PlotModel] = relationship(back_populates="aliases")


class ImportBatchModel(Base):
    __tablename__ = "import_batches"

    import_batch_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="excel")
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parse_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    observations: Mapped[list["MetricObservationModel"]] = relationship(back_populates="import_batch")
    issues: Mapped[list["ImportIssueModel"]] = relationship(
        back_populates="import_batch",
        cascade="all, delete-orphan",
    )


class MetricObservationModel(Base):
    __tablename__ = "metric_observations"
    __table_args__ = (
        Index("ix_metric_observations_plot_metric_date", "plot_id", "metric_code", "observed_at"),
        Index("ix_metric_observations_metric_date", "metric_code", "observed_at"),
        Index("ix_metric_observations_import_batch_id", "import_batch_id"),
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.plot_id"), nullable=False)
    plot_code: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_code: Mapped[str] = mapped_column(ForeignKey("metrics.metric_code"), nullable=False)
    value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_at: Mapped[date] = mapped_column(Date, nullable=False)
    import_batch_id: Mapped[str] = mapped_column(ForeignKey("import_batches.import_batch_id"), nullable=False)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_sheet: Mapped[str | None] = mapped_column(String(255))
    raw_cell: Mapped[str | None] = mapped_column(String(32))
    quality_flag: Mapped[str] = mapped_column(String(32), nullable=False, default="normal", index=True)

    plot: Mapped[PlotModel] = relationship(back_populates="observations")
    metric: Mapped[MetricModel] = relationship(back_populates="observations")
    import_batch: Mapped[ImportBatchModel] = relationship(back_populates="observations")


class ImportIssueModel(Base):
    __tablename__ = "import_issues"
    __table_args__ = (
        Index("ix_import_issues_import_batch_id", "import_batch_id"),
        Index("ix_import_issues_type_severity", "issue_type", "severity"),
    )

    issue_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    import_batch_id: Mapped[str] = mapped_column(ForeignKey("import_batches.import_batch_id", ondelete="CASCADE"), nullable=False)
    issue_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_sheet: Mapped[str | None] = mapped_column(String(255))
    raw_cell: Mapped[str | None] = mapped_column(String(32))
    plot_code: Mapped[str | None] = mapped_column(String(128))
    metric_code: Mapped[str | None] = mapped_column(String(64))

    import_batch: Mapped[ImportBatchModel] = relationship(back_populates="issues")
