from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from database import Base




class Telegram(Base):
    __tablename__ = "telegram"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True)