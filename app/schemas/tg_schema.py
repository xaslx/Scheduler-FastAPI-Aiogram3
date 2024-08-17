from pydantic import BaseModel



class TelegramIn(BaseModel):
    telegram_id: int