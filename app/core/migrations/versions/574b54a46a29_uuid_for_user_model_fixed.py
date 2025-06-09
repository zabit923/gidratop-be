"""uuid_for_user_model_fixed

Revision ID: 574b54a46a29
Revises: 2ccff15fe673
Create Date: 2025-06-07 18:57:32.665662

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "574b54a46a29"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Проверяем существование enum типов
    connection = op.get_bind()

    # Проверяем существование userrole enum
    userrole_exists = connection.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'userrole'")
    ).fetchone()

    # Проверяем существование paymenttype enum
    paymenttype_exists = connection.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'paymenttype'")
    ).fetchone()

    # Создаем enum только если не существует
    if not userrole_exists:
        op.execute("CREATE TYPE userrole AS ENUM ('ADMIN', 'MODERATOR', 'USER')")

    if not paymenttype_exists:
        op.execute("CREATE TYPE paymenttype AS ENUM ('CARD', 'CASH', 'ONLINE', 'WALLET')")

    # Удаляем старые таблицы если существуют
    op.execute("DROP TABLE IF EXISTS user_addresses CASCADE")
    op.execute("DROP TABLE IF EXISTS payment_methods CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    # Создаем таблицы заново с UUID
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("ADMIN", "MODERATOR", "USER", name="userrole"),
            nullable=False,
        ),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("middle_name", sa.String(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("avatar", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("bonus_points", sa.Integer(), nullable=False),
        sa.Column(
            "cashback_balance", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.Column("email_notifications", sa.Boolean(), nullable=False),
        sa.Column("sms_notifications", sa.Boolean(), nullable=False),
        sa.Column("push_notifications", sa.Boolean(), nullable=False),
        sa.Column("marketing_consent", sa.Boolean(), nullable=False),
        sa.Column("referral_code", sa.String(), nullable=True),
        sa.Column("referred_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("total_orders", sa.Integer(), nullable=False),
        sa.Column("total_spent", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("last_order_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("registration_source", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["referred_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("referral_code"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "payment_methods",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "payment_type",
            postgresql.ENUM("CARD", "CASH", "ONLINE", "WALLET", name="paymenttype"),
            nullable=False,
        ),
        sa.Column("card_last_four", sa.String(), nullable=True),
        sa.Column("card_brand", sa.String(), nullable=True),
        sa.Column("card_token", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_addresses",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("street", sa.String(), nullable=False),
        sa.Column("house", sa.String(), nullable=False),
        sa.Column("apartment", sa.String(), nullable=True),
        sa.Column("entrance", sa.String(), nullable=True),
        sa.Column("floor", sa.String(), nullable=True),
        sa.Column("postal_code", sa.String(), nullable=True),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_addresses")
    op.drop_table("payment_methods")
    op.drop_table("users")
