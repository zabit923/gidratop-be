from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseModel


class Card(BaseModel):
    """
    Модель карточки.
    """

    __tablename__ = "cards"
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    image: Mapped[Optional[str]] = mapped_column(
        nullable=True, default=None, server_default=None
    )
