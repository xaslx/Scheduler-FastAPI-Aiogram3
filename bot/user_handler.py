from datetime import datetime, date
from re import T
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram.fsm.state import default_state
from aiogram.types import Message
from app.schemas.user_schema import UserOut
from bot.bot_service import BotService
from app.schemas.tg_schema import TelegramOut
from app.utils.generate_time import moscow_tz
from app.schemas.booking_schemas import BookingOut
from bot.keyboards import create_inline_button


user_router: Router = Router()



@user_router.message(CommandStart(), StateFilter(default_state))
async def cmd_start(message: Message):
    await message.answer('Привет, это Бот от сайта Scheduler\nВаш ID, скопируйте его и вставьте на сайте')
    await message.answer(str(message.from_user.id))
    user: TelegramOut = await BotService.find_user_by_tg_id(telegram_id=message.from_user.id)
    if not user:
        await BotService.add_new_user(telegram_id=message.from_user.id)


@user_router.message(StateFilter(default_state), Command('clients'))
async def my_clients(message: Message):
    user: UserOut = await BotService.find_user(telegram_id=message.from_user.id)
    if not user:
        await message.answer('Вы не привязали свой телеграм к профилю на сайте')
        return
    res: list[BookingOut] = await BotService.get_all_bookings(user_id=user.id, date=datetime.now(tz=moscow_tz).date())
    for booking in res:
        await message.answer(f'{booking.date_for_booking}, <b>количество записанных пользователей: {len(booking.selected_times)}</b>')
    await message.answer(
        f'Введите /date "ДАТА"\n'
        f'Чтобы посмотреть забронированное время\n\n'
        f'Пример: /date 01.01.2024'
    )


@user_router.message(StateFilter(default_state), Command('date'))
async def get_clients_by_date(message: Message, command: CommandObject):
    user: UserOut = await BotService.find_user(telegram_id=message.from_user.id)
    if not user:
        await message.answer('Вы не привязали свой телеграм к профилю на сайте')
    else:
        try:
            date_object: BookingOut = datetime.strptime(command.args, "%d.%m.%Y").date()
        except:
            await message.answer(f'Неверная дата, введите в формате: День.Месяц.Год\nПример: /date 01.01.2024')
        else:
            clients: BookingOut = await BotService.get_booking(user_id=user.id, date=date_object)
            if not clients:
                await message.answer('На выбранную дату нет клиентов')
            else:
                await message.answer(
                    f'Все записи на : {date_object}',
                    reply_markup=await create_inline_button(clients.selected_times)
                )

@user_router.message(StateFilter(default_state), Command('help'))
async def help_command(message: Message):
    await message.answer(
        f'<b>Все доступные команды</b>\n\n'
        f'/start  -  Получить свой ID\n'
        f'/clients  -  Посмотреть ближайших клиентов\n'
        f'/date  * Дата *  -  Посмотреть забронированное время на определенную дату'
    )


@user_router.message(StateFilter(default_state))
async def echo(message: Message):
    await message.answer(
        "Это неизвестная команда. Чтобы посмотреть все доступные команды введите /help"
    )