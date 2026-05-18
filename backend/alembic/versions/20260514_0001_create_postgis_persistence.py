"""create postgis persistence tables

Revision ID: 20260514_0001
Revises:
Create Date: 2026-05-14 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


revision: str = "20260514_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "metrics",
        sa.Column("metric_code", sa.String(length=64), nullable=False),
        sa.Column("metric_name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("value_type", sa.String(length=16), nullable=False),
        sa.Column("precision", sa.Integer(), nullable=False),
        sa.Column("normal_min", sa.Float(), nullable=False),
        sa.Column("normal_max", sa.Float(), nullable=False),
        sa.Column("color_scale", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("metric_code"),
    )

    op.create_table(
        "plots",
        sa.Column("plot_id", sa.String(length=128), nullable=False),
        sa.Column("plot_code", sa.String(length=128), nullable=False),
        sa.Column("plot_name", sa.String(length=255), nullable=True),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="GEOMETRY",
                srid=4326,
                spatial_index=False,
            ),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("plot_id"),
    )
    op.create_index("ix_plots_plot_code", "plots", ["plot_code"], unique=False)
    op.create_index("ix_plots_region", "plots", ["region"], unique=False)
    op.create_index("ix_plots_status", "plots", ["status"], unique=False)
    op.create_index("ix_plots_geometry", "plots", ["geometry"], unique=False, postgresql_using="gist")

    op.create_table(
        "import_batches",
        sa.Column("import_batch_id", sa.String(length=128), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column("warning_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("skipped_record_count", sa.Integer(), nullable=False),
        sa.Column("parse_duration_ms", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("import_batch_id"),
    )
    op.create_index("ix_import_batches_status", "import_batches", ["status"], unique=False)

    op.create_table(
        "plot_aliases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plot_id", sa.String(length=128), nullable=False),
        sa.Column("alias", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(["plot_id"], ["plots.plot_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias", "plot_id", name="uq_plot_aliases_alias_plot_id"),
    )
    op.create_index("ix_plot_aliases_alias", "plot_aliases", ["alias"], unique=False)

    op.create_table(
        "metric_observations",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("plot_id", sa.String(length=128), nullable=False),
        sa.Column("plot_code", sa.String(length=128), nullable=False),
        sa.Column("metric_code", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("observed_at", sa.Date(), nullable=False),
        sa.Column("import_batch_id", sa.String(length=128), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("raw_sheet", sa.String(length=255), nullable=True),
        sa.Column("raw_cell", sa.String(length=32), nullable=True),
        sa.Column("quality_flag", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.import_batch_id"]),
        sa.ForeignKeyConstraint(["metric_code"], ["metrics.metric_code"]),
        sa.ForeignKeyConstraint(["plot_id"], ["plots.plot_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metric_observations_import_batch_id", "metric_observations", ["import_batch_id"], unique=False)
    op.create_index("ix_metric_observations_metric_date", "metric_observations", ["metric_code", "observed_at"], unique=False)
    op.create_index("ix_metric_observations_plot_metric_date", "metric_observations", ["plot_id", "metric_code", "observed_at"], unique=False)
    op.create_index("ix_metric_observations_quality_flag", "metric_observations", ["quality_flag"], unique=False)

    op.create_table(
        "import_issues",
        sa.Column("issue_id", sa.String(length=128), nullable=False),
        sa.Column("import_batch_id", sa.String(length=128), nullable=False),
        sa.Column("issue_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("raw_sheet", sa.String(length=255), nullable=True),
        sa.Column("raw_cell", sa.String(length=32), nullable=True),
        sa.Column("plot_code", sa.String(length=128), nullable=True),
        sa.Column("metric_code", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.import_batch_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("issue_id"),
    )
    op.create_index("ix_import_issues_import_batch_id", "import_issues", ["import_batch_id"], unique=False)
    op.create_index("ix_import_issues_type_severity", "import_issues", ["issue_type", "severity"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_import_issues_type_severity", table_name="import_issues")
    op.drop_index("ix_import_issues_import_batch_id", table_name="import_issues")
    op.drop_table("import_issues")
    op.drop_index("ix_metric_observations_quality_flag", table_name="metric_observations")
    op.drop_index("ix_metric_observations_plot_metric_date", table_name="metric_observations")
    op.drop_index("ix_metric_observations_metric_date", table_name="metric_observations")
    op.drop_index("ix_metric_observations_import_batch_id", table_name="metric_observations")
    op.drop_table("metric_observations")
    op.drop_index("ix_plot_aliases_alias", table_name="plot_aliases")
    op.drop_table("plot_aliases")
    op.drop_index("ix_import_batches_status", table_name="import_batches")
    op.drop_table("import_batches")
    op.drop_index("ix_plots_geometry", table_name="plots")
    op.drop_index("ix_plots_status", table_name="plots")
    op.drop_index("ix_plots_region", table_name="plots")
    op.drop_index("ix_plots_plot_code", table_name="plots")
    op.drop_table("plots")
    op.drop_table("metrics")
