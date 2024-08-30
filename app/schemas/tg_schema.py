from pydantic import BaseModel


class Telegram(BaseModel):
    telegram_id: int

class TelegramOut(Telegram):
    id: int
