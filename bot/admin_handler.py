from aiogram import Router
from aiogram.filters import Command, StateFilter
from app.schemas.tg_schema import TelegramOut
from bot.bot_service import BotService
from aiogram.types import Message
from aiogram.fsm.state import default_state
from bot.admin_filter import AdminProtect
from bot.state_for_admin import CreateNotification
from aiogram.fsm.context import FSMContext
from app.tasks.tasks import send_notifications_for_all_users_tg

admin_router: Router = Router()


@admin_router.message(StateFilter(default_state), AdminProtect(), Command("apanel"))
async def admins_panel(message: Message):
    await message.answer(
        "Команды администраторов:\n/create_notification  -  Отправить рассылку"
    )


@admin_router.message(
    StateFilter(default_state), AdminProtect(), Command(commands="acancel")
)
async def process_cancel_command(message: Message):
    await message.answer(
        text="Отменять нечего. Вы пока не создаете уведомление\n\n"
        "Чтобы перейти к созданию уведомления\n"
        "отправьте команду /create_notification"
    )


@admin_router.message(
    ~StateFilter(default_state), AdminProtect(), Command(commands="acancel")
)
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text="Вы отменили создание уведомления\n\n"
        "Чтобы снова перейти к созданию уведомления\n"
        "отправьте команду /create_notification"
    )
    await state.clear()


@admin_router.message(
    StateFilter(default_state), AdminProtect(), Command("create_notification")
)
async def create_notification(message: Message, state: FSMContext):
    await state.set_state(CreateNotification.description)
    await message.answer(
        "Напишите сообщение, его увидят все пользователи которые пользуются ботом\n/acancel - Для отмены создания уведомления"
    )


@admin_router.message(StateFilter(CreateNotification.description), AdminProtect())
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    users: list[TelegramOut] = await BotService.find_all_users()
    await message.answer(
        f"Уведомление создано и будет отправлено пользователям\n"
        f"Количество пользователей которые получат уведомление:  {len(users)}"
    )
    text: str = await state.get_data()
    await state.clear()
    await send_notifications_for_all_users_tg(users_id=users, text=text["description"])
