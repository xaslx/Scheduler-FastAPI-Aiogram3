from app.repository.base_repo import BaseRepository
from app.models.telegram_model import Telegram


class TelegramRepository(BaseRepository):
    model = Telegram
