"""add is_active to punto_peaje

Revision ID: ddf2456983a6
Revises: ce247d64f266
Create Date: 2026-08-04 08:32:26.485903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddf2456983a6'
down_revision: Union[str, Sequence[str], None] = 'ce247d64f266'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
