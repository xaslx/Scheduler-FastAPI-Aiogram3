from datetime import datetime, date, time
from http import client
from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import desc
from app.schemas.user_schema import UserOut
from bot.bot_service import BotService
from app.schemas.tg_schema import TelegramOut
from app.utils.generate_time import moscow_tz
from app.schemas.booking_schemas import BookingOut
from bot.keyboards import create_inline_button, confirmation_markup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.schemas.booking_schemas import CancelBooking
from config import settings
from aiogram.client.default import DefaultBotProperties

user_router: Router = Router()

bot: Bot = Bot(settings.TOKEN_BOT, default=DefaultBotProperties(parse_mode='HTML'))


@user_router.callback_query(F.data.startswith('cancel'))
async def cancel_booking(callback: CallbackQuery):
    await callback.answer()
    _, booking_id, user_id, date_, hour, minute = callback.data.split(':')
    user: UserOut = await BotService.find_user(telegram_id=callback.from_user.id)
    if not user:
        await callback.message.answer('Вы не подключили свой телеграм к профилю на сайте')
    else:
        inline_kb: InlineKeyboardMarkup = confirmation_markup(
            booking_id=booking_id, 
            user_id=user_id,
            date_=date_,
            hour=hour,
            minute=minute
        )
        await callback.message.edit_text(
            f'Вы уверенны что хотите отменить запись?\n'
            f'на время: <b>{hour}:{minute}</b> и дату: <b>{date_}</b>',
            reply_markup=inline_kb
        )

@user_router.callback_query(F.data == 'action_cancel')
async def cancel_action(callback: CallbackQuery):
    await callback.answer()
    user: UserOut = await BotService.find_user(telegram_id=callback.from_user.id)
    if not user:
        await callback.message.answer('Вы не подключили свой телеграм к профилю на сайте')
    else:
        await callback.message.edit_text(f'<b>Вы решили не отменять запись</b>')

@user_router.callback_query(F.data.startswith('confirm_cancel'))
async def confirm_cancel_booking(callback: CallbackQuery):
    await callback.answer()
    _, _, _, date_, hour, minute = callback.data.split(':')
    date_obj = datetime.strptime(date_, '%d.%m.%Y').date()
    formatted_time: str = str(time(hour=int(hour), minute=int(minute)).strftime('%H:%M'))
    user: UserOut = await BotService.find_user(telegram_id=callback.from_user.id)
    if not user:
        await callback.message.answer('Вы не подключили свой телеграм к профилю на сайте')
    else:
        booking: BookingOut = await BotService.get_booking(user_id=user.id, date=date_obj)
        cancel_booking: CancelBooking | None = None
        if not booking:
            await callback.message.answer('Запись не найдена')
        else:
            for client in booking.selected_times:
                if client[0] == formatted_time:
                    cancel_booking: CancelBooking = CancelBooking(
                        date=str(date_obj),
                        time=client[0],
                        email=client[3],
                        description='Отмена через Телеграм бота',
                        name=client[1],
                        phone_number=client[2],
                        tg_id=str(callback.from_user.id)
                    )
                    break
        try:
            await BotService.cancel_booking(user_id=user.id, booking_id=booking.id, time=formatted_time)
        except:
            await callback.message.answer('Не удалось отменить запись.')
        else:
            await callback.message.edit_text('<b>Вы успешно отменили запись.</b>')
            await callback.message.answer(
                f'<b>Вы отменили запись у пользователя</b>\n'
                f'<b>Инфо о пользователе:</b>\n'
                f'Имя: <b>{cancel_booking.name}</b>\n'
                f'Email: <b>{cancel_booking.email}</b>\n'
                f'Телефон: <b>{cancel_booking.phone_number}</b>\n'
                f'Телеграм ID: <b>{cancel_booking.tg_id}</b>\n\n'
                f'Дата: <b>{date_}</b>\n'
                f'Время: <b>{formatted_time}</b>'
            )
            await bot.send_message(
                chat_id=int(cancel_booking.tg_id),
                text=
                f'<b>Вам отменили запись</b>\n'
                f'Дата: <b>{date_}</b>\n'
                f'Время: <b>{formatted_time}</b>\n'
                f'Причина: <b>{cancel_booking.description}</b>'
            )


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
    exist_booking: bool = False
    for booking in res:
        if len(booking.selected_times) > 0:
            exist_booking = True
            await message.answer(
                f'{datetime.strftime(booking.date_for_booking, '%d.%m.%Y')}, <b>количество записанных пользователей: {len(booking.selected_times)}</b>'
            )
    if not exist_booking:
        await message.answer('Нет ближайших записей')
    else:
        await message.answer(
            f'Введите /date  <i>дату</i>\n'
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
            if (not clients) or (len(clients.selected_times) <= 0):
                await message.answer('На выбранную дату нет клиентов')
            else:
                inline_kb: InlineKeyboardBuilder = create_inline_button(
                        clients.selected_times,
                        booking_id=clients.id,
                        user_id=user.id,
                        date=command.args)
                await message.answer(
                    f'Все записи на : <b>{command.args}</b>\n'
                    f'<b>Чтобы отменить запись нажмите на время, которое хотите отменить</b>',
                    reply_markup=inline_kb
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