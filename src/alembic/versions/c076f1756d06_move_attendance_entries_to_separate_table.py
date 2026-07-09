"""Move attendance entries to separate table

Revision ID: c076f1756d06
Revises: 856c22036c6b
Create Date: 2026-07-09 10:48:40.054300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c076f1756d06'
down_revision: Union[str, None] = '856c22036c6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attendance_entry",
        sa.Column("practice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("planned_attendance", sa.Boolean(), nullable=True),
        sa.Column("actual_attendance", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["practice_id"], ["attendance.practice_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("practice_id", "user_id"),
    )

    op.execute(
        """
        INSERT INTO attendance_entry (practice_id, user_id, planned_attendance, actual_attendance)
        SELECT
            a.practice_id,
            (elem->>'user_id')::uuid,
            (elem->>'planned_attendance')::boolean,
            (elem->>'actual_attendance')::boolean
        FROM attendance a,
             jsonb_array_elements(a.attendance_list::jsonb) AS elem
        """
    )

    op.drop_column("attendance", "attendance_list")

    
    op.create_foreign_key(
        "fk_practice_team_id",
        "practice",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_user_role_team_id",
        "user_role",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_user_role_user_id",
        "user_role",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_attendance_entry_user_id",
        "attendance_entry",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_attendance_entry_user_id", "attendance_entry", type_="foreignkey")
    op.drop_constraint("fk_user_role_user_id", "user_role", type_="foreignkey")
    op.drop_constraint("fk_user_role_team_id", "user_role", type_="foreignkey")
    op.drop_constraint("fk_practice_team_id", "practice", type_="foreignkey")

    op.add_column(
        "attendance",
        sa.Column(
            "attendance_list",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )

    op.execute(
        """
        UPDATE attendance a
        SET attendance_list = sub.entries
        FROM (
            SELECT
                practice_id,
                jsonb_agg(
                    jsonb_build_object(
                        'user_id', user_id,
                        'planned_attendance', planned_attendance,
                        'actual_attendance', actual_attendance
                    )
                ) AS entries
            FROM attendance_entry
            GROUP BY practice_id
        ) sub
        WHERE a.practice_id = sub.practice_id
        """
    )

    op.drop_table("attendance_entry")
