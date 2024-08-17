from aiogram import Router
from aiogram.filters import Filter, Command, StateFilter
from config import settings
from aiogram.types import Message
from aiogram.fsm.state import default_state
from bot.admin_filter import AdminProtect


admin_router: Router = Router()


@admin_router.message(StateFilter(default_state), AdminProtect(), Command('apanel'))
async def admins_panel(message: Message):
    await message.answer('Команды администраторов:\n/create_notifications  -  Отправить рассылку')


