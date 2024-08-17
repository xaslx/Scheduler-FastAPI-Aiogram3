from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from bot.bot_service import BotService
from app.schemas.tg_schema import TelegramOut


user_router: Router = Router()



@user_router.message(CommandStart(), StateFilter(default_state))
async def cmd_start(message: Message):
    await message.answer('Привет, это Бот от сайта Scheduler\nВаш ID, скопируйте его и вставьте на сайте')
    await message.answer(str(message.from_user.id))
    user: TelegramOut = await BotService.find_user_by_tg_id(telegram_id=message.from_user.id)
    if not user:
        await BotService.add_new_user(telegram_id=message.from_user.id)




