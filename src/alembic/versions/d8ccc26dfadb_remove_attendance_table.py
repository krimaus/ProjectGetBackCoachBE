"""Remove attendance table

Revision ID: d8ccc26dfadb
Revises: c076f1756d06
Create Date: 2026-07-09 12:55:26.312262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8ccc26dfadb'
down_revision: Union[str, None] = 'c076f1756d06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('practice', sa.Column('notes', sa.String(), nullable=True))

    op.execute(
        """
        UPDATE practice p
        SET notes = a.notes
        FROM attendance a
        WHERE p.id = a.practice_id
        """
    )

    op.drop_constraint(
        op.f('attendance_entry_practice_id_fkey'), 'attendance_entry', type_='foreignkey'
    )

    op.drop_table('attendance')

    op.create_foreign_key(
        'attendance_entry_practice_id_fkey',
        'attendance_entry', 'practice', ['practice_id'], ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint(
        'attendance_entry_practice_id_fkey', 'attendance_entry', type_='foreignkey'
    )

    op.create_table(
        'attendance',
        sa.Column('practice_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('notes', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('practice_id', name=op.f('attendance_pkey')),
    )

    op.execute(
        """
        INSERT INTO attendance (practice_id, notes)
        SELECT DISTINCT p.id, p.notes
        FROM practice p
        JOIN attendance_entry ae ON ae.practice_id = p.id
        """
    )

    op.create_foreign_key(
        op.f('attendance_entry_practice_id_fkey'),
        'attendance_entry', 'attendance', ['practice_id'], ['practice_id'],
        ondelete='CASCADE',
    )

    op.drop_column('practice', 'notes')
