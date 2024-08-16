from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from fastapi import Depends
from database import get_async_session, async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.notification_repo import NotificationRepository
from app.repository.user_repo import UserRepository

user_router: Router = Router()



@user_router.message(CommandStart(), StateFilter(default_state))
async def cmd_start(message: Message):
    await message.answer('Привет, это Бот от сайта Scheduler')
    await message.answer('Ваш ID, скопируйте его и вставьте на сайте')
    await message.answer(str(message.from_user.id))




