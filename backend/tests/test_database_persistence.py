from __future__ import annotations

from pathlib import Path

from geoalchemy2 import Geometry

from app.models import Base, ImportBatchModel, ImportIssueModel, MetricObservationModel, PlotAliasModel, PlotModel


def test_database_metadata_defines_required_persistence_tables():
    assert set(Base.metadata.tables) >= {
        "metrics",
        "plots",
        "plot_aliases",
        "metric_observations",
        "import_batches",
        "import_issues",
    }


def test_plot_model_uses_postgis_geometry_and_alias_mapping_constraints():
    geometry_type = PlotModel.__table__.c.geometry.type
    alias_constraints = {
        constraint.name
        for constraint in PlotAliasModel.__table__.constraints
        if constraint.name
    }

    assert isinstance(geometry_type, Geometry)
    assert geometry_type.srid == 4326
    assert "uq_plot_aliases_alias_plot_id" in alias_constraints


def test_observations_keep_traceability_foreign_keys_and_indexes():
    columns = MetricObservationModel.__table__.c
    index_names = {index.name for index in MetricObservationModel.__table__.indexes}

    assert columns.plot_id.foreign_keys
    assert columns.metric_code.foreign_keys
    assert columns.import_batch_id.foreign_keys
    assert {"import_batch_id", "quality_flag"} <= set(columns.keys())
    assert "ix_metric_observations_plot_metric_date" in index_names
    assert "ix_metric_observations_metric_date" in index_names


def test_legacy_tables_are_mapped_to_observation_batch_and_quality_issue_semantics():
    batch_columns = ImportBatchModel.__table__.c
    issue_columns = ImportIssueModel.__table__.c

    assert {"import_batch_id", "source_type", "record_count", "warning_count", "error_count"} <= set(batch_columns.keys())
    assert {"issue_id", "import_batch_id", "issue_type", "severity", "message"} <= set(issue_columns.keys())


def test_initial_alembic_revision_enables_postgis_and_creates_spatial_index():
    migration = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "20260514_0001_create_postgis_persistence.py"
    ).read_text(encoding="utf-8")

    assert "CREATE EXTENSION IF NOT EXISTS postgis" in migration
    assert "ix_plots_geometry" in migration
    assert "postgresql_using=\"gist\"" in migration
