"""make person user optional

Revision ID: bc4d2f1a9c3e
Revises: 7bd7429a3e8d
Create Date: 2026-05-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bc4d2f1a9c3e"
down_revision: Union[str, Sequence[str], None] = "7bd7429a3e8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("persons_user_id_fkey", "persons", type_="foreignkey")
    op.alter_column(
        "persons",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_foreign_key(
        "persons_user_id_fkey",
        "persons",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("persons_user_id_fkey", "persons", type_="foreignkey")
    op.alter_column(
        "persons",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "persons_user_id_fkey",
        "persons",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
