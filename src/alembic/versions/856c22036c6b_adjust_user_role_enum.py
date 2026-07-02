"""Adjust UserRoleEnum

Revision ID: 856c22036c6b
Revises: e94fa4bff8ef
Create Date: 2026-07-02 08:15:51.680802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '856c22036c6b'
down_revision: Union[str, None] = 'e94fa4bff8ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        # 1. add OWNER first so it's usable below
        op.execute("ALTER TYPE user_role_enum ADD VALUE IF NOT EXISTS 'OWNER'")

        # 2. reassign rows that use the value we're about to remove
        op.execute("UPDATE user_role SET role = 'OWNER' WHERE role = 'ADMIN'")

        # 3. rebuild the enum without ADMIN
        op.execute("ALTER TYPE user_role_enum RENAME TO user_role_enum_old")
        op.execute(
            "CREATE TYPE user_role_enum AS ENUM('COACH', 'MEMBER', 'OWNER')"
        )
        op.execute(
            "ALTER TABLE user_role "
            "ALTER COLUMN role TYPE user_role_enum "
            "USING role::text::user_role_enum"
        )
        op.execute("DROP TYPE user_role_enum_old")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        # 1. add ADMIN back so it's usable below
        op.execute("ALTER TYPE user_role_enum ADD VALUE IF NOT EXISTS 'ADMIN'")

        # 2. reassign rows that use the value we're about to remove
        op.execute("UPDATE user_role SET role = 'ADMIN' WHERE role = 'OWNER'")

        # 3. rebuild the enum without OWNER
        op.execute("ALTER TYPE user_role_enum RENAME TO user_role_enum_old")
        op.execute(
            "CREATE TYPE user_role_enum AS ENUM('ADMIN', 'COACH', 'MEMBER')"
        )
        op.execute(
            "ALTER TABLE user_role "
            "ALTER COLUMN role TYPE user_role_enum "
            "USING role::text::user_role_enum"
        )
        op.execute("DROP TYPE user_role_enum_old")
