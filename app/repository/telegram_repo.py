from app.models.telegram_model import Telegram
from app.repository.base_repo import BaseRepository


class TelegramRepository(BaseRepository):
    model = Telegram
