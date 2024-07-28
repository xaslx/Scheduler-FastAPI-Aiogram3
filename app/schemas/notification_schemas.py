from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateNotification(BaseModel):
    title: str = Field(min_length=5, max_length=60)
    description: str = Field(min_length=15, max_length=500)


class NotificationOut(BaseModel):
    id: int
    created_at: datetime
    title: str
    description: str

    model_config = ConfigDict(from_attributes=True)
