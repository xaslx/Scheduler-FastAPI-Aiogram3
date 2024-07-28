from database import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime, String
from app.utils.generate_time import moscow_tz
from app.utils.current_time import current_time



class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=current_time)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(500))

