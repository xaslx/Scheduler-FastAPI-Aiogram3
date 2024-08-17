from pydantic import BaseModel



class TelegramOut(BaseModel):
    id: int
    telegram_id: int