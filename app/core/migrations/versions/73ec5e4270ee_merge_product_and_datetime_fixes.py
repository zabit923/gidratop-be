"""Merge product and datetime fixes

Revision ID: 73ec5e4270ee
Revises: 1bc2215be7ef, 2ccff15fe673
Create Date: 2025-05-31 16:43:36.581146

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "73ec5e4270ee"
down_revision: Union[str, None] = ("1bc2215be7ef", "2ccff15fe673")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
