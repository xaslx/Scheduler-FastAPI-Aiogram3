from datetime import datetime, date, time, timedelta
from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from app.schemas.user_schema import UserOut
from bot.bot_service import BotService
from app.auth.authentication import generate_token_connect_tg
from app.schemas.tg_schema import TelegramOut
from app.utils.generate_time import moscow_tz
from app.schemas.booking_schemas import BookingOut
from bot.keyboards import create_inline_button, confirmation_markup, create_inline_button_times, create_inline_button_connect_tg
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.schemas.booking_schemas import CancelBooking
from config import settings
from aiogram.client.default import DefaultBotProperties
from bot.state import NewBooking
from aiogram.fsm.context import FSMContext
from email_validator import validate_email, EmailNotValidError
from app.utils.generate_time import generate_time_intervals


user_router: Router = Router()

bot: Bot = Bot(settings.TOKEN_BOT, default=DefaultBotProperties(parse_mode='HTML'))



@user_router.message(Command(commands="cancel"), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text="Отменять нечего.\n\n"
        "Отправьте команду /new"
    )


@user_router.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text="Вы отменили создание записи\n\n"
        "Чтобы снова перейти к созданию записи - "
        "отправьте команду /new"
    )
    await state.clear()


@user_router.message(StateFilter(default_state), Command('new'))
async def create_new_booking(message: Message, state: FSMContext):
    await state.set_state(NewBooking.personal_link)
    await state.update_data(tg_username=message.from_user.username if message.from_user.username else 'Скрыт')
    await message.answer('Введите ссылку для записи или /cancel для отмены')


@user_router.message(StateFilter(NewBooking.personal_link), F.text)
async def create_new_booking(message: Message, state: FSMContext):
    personal_link: str = message.text
    if 'scheduler' in message.text:
        personal_link: str = message.text.split('/')[-1]
    user: UserOut = await BotService.find_user(personal_link=personal_link)
    if not user:
        return await message.answer('Не удалось найти пользователя по ссылке')
    elif not user.is_active:
        return await message.answer(
            'Нельзя записаться к пользователю\n'
            'Так как он заблокирован'
        )
    else:
        await message.answer(
            f'Пользователь найден\n'
            f'Имя: <b>{user.name}</b>\nФамилия: <b>{user.surname}</b>'
        )
        await message.answer(
            'Теперь введите дату на которую хотите записаться\n'
            'Дата должна быть в формате <b>ДД.ММ.ГГ</b>\n'
            'Например <b>01.01.2000</b>\n'
            'Или введите /cancel - для отмены'
        )
        await state.update_data(personal_link=personal_link)
        await state.set_state(NewBooking.date)

@user_router.message(StateFilter(NewBooking.personal_link), ~F.text)
async def create_new_booking(message: Message):
    await message.answer('Ссылка должна быть в виде текста.')


@user_router.message(StateFilter(NewBooking.date), F.text)
async def set_date(message: Message, state: FSMContext):
    await state.update_data(tg_id=message.from_user.id)
    try:
        formated_date: date = datetime.strptime(message.text, '%d.%m.%Y').date()
        today_date: date = datetime.now(tz=moscow_tz).date()
        if (formated_date - today_date).days > 7:
            return await message.answer('Можно выбрать дату максимум на неделю вперед.')
        if formated_date < today_date:
            return await message.answer('Нельзя выбрать прошедшую дату.')
        await state.update_data(date=formated_date)
    except:
        await message.answer(
            'Введите корректную дату\n'
            'В формате <b>ДД.ММ.ГГ</b>\n'
            'Например <b>01.01.2000</b>\n'
            'Или /cancel - для отмены'
        )
    else:
        result: dict = await state.get_data()
        user: UserOut = await BotService.find_user(personal_link=result['personal_link'])
        await state.update_data(user_email=user.email, user_tg=user.telegram_link if user.telegram_link else 'Не указан')
        booking: BookingOut = await BotService.get_booking(user_id=user.id, date=formated_date)
        await state.update_data(user_tg_id=user.telegram_id)
        if not booking:
            intervals: list[str] = await generate_time_intervals(
                user.start_time, user.end_time, user.interval
            )
            booking_id: int = await BotService.add_booking(date_for_booking=result['date'], user_id=user.id, times=intervals)
            booking: BookingOut = await BotService.get_booking(user_id=user.id, date=result['date'])
        now: datetime = datetime.now(tz=moscow_tz)
        current_time: str = now.strftime("%H:%M")
        current_date = now.date()

        if booking.date_for_booking == current_date:
            available_times = [time for time in booking.times if time > current_time]
        else:
            available_times = booking.times
        if len(available_times) > 0:
            inline_kb = create_inline_button_times(times=available_times, booking_id=booking.id, user_id=booking.user_id, date=result['date'])
            await message.answer(
                'Теперь выберите время для записи. <b>Указано по Москве</b>',
                reply_markup=inline_kb
                
            )
            await state.set_state(NewBooking.time)
        else:
            return await message.answer('На выбранную дату не осталось свободного времени')

        

@user_router.message(StateFilter(NewBooking.date), ~F.text)
async def set_date_warning(message: Message):
    await message.answer(
        'Дата должна быть в виде текста\n'
        'Если хотите отменить введите /cancel'
    )


@user_router.callback_query(StateFilter(NewBooking.time), F.data.startswith('select'))
async def set_time(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    _, booking_id, user_id, date_, hour, minute = callback.data.split(':')
    await state.update_data(booking_id=booking_id, user_id=user_id, time=f'{hour}:{minute}')
    await callback.message.edit_text(f'Вы выбрали время: <b>{hour}:{minute}.</b>\nТеперь введите ваше имя.\nИли /cancel - если хотите отменить')
    await state.set_state(NewBooking.name)



@user_router.message(StateFilter(NewBooking.name), (F.text & F.text.regexp(r'^.{2,20}$')))
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        'Введите ваш email\n'
        'Или /cancel - если хотите отменить'
    )
    await state.set_state(NewBooking.email)

@user_router.message(StateFilter(NewBooking.name), ~(F.text & F.text.regexp(r'^.{2,20}$')))
async def set_name_warning(message: Message):
    await message.answer(
        'Введите корректное имя\n'
        'Имя должно быть мин. 2 буквы, макс. 20\n'
        'Или введите /cancel - для отмены'
    )

@user_router.message(StateFilter(NewBooking.email), F.text)
async def set_email(message: Message, state: FSMContext):
    try:
        validate_email(message.text)
        await state.update_data(email=message.text)
        await message.answer(
            'Теперь введите ваш телефон\n'
            'Или /cancel - для отмены'
        )
        await state.set_state(NewBooking.phone_number)
    except EmailNotValidError:
        return await message.answer('Введен неккоректный Email')

@user_router.message(StateFilter(NewBooking.email), ~F.text)
async def set_email_warning(message: Message):
    await message.answer('Email должен быть в виде текста')


@user_router.message(StateFilter(NewBooking.phone_number), (F.text & F.text.regexp(r'^.{10,11}$')))
async def set_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    res = await state.get_data()
    await BotService.new_booking(
        user_id=int(res['user_id']), 
        booking_id=int(res['booking_id']), 
        time=(res['time'], res['name'], res['phone_number'], res['email'], message.from_user.id))
    await message.answer(
        f'Вы успешно записались на время: <b>{res['time']}</b>\n'
        f'Дата: <b>{res['date'].strftime('%d.%m.%Y')}</b>\n\n'
        f'Если хотите отменить запись то напишите на Email: <b>{res['user_email']}</b>\n'
        f'Или Телеграм: <b>{res['user_tg']}</b>'
    )
    await state.clear()
    if res['user_tg_id']:
        await bot.send_message(
            res['user_tg_id'], 
            text=
            f'К вам записался новый клиент!\n'
            f'Дата: <b>{res['date'].strftime('%d.%m.%Y')}</b>\n'
            f'Время: <b>{res['time']}</b>\n\n'
            f'<b>Информация о клиенте</b>\n'
            f'Имя: <b>{res['name']}</b>\n'
            f'Телефон: <b>{res['phone_number']}</b>\n'
            f'Email клиента: <b>{res['email']}</b>\n'
            f'Telegram: <b>{res['tg_username']}</b>\n\n'
            f'Введите /clients - чтобы посмотреть ваших клиентов, также там можно отменить запись'
        )
        
    


@user_router.message(StateFilter(NewBooking.phone_number), ~(F.text & F.text.regexp(r'^.{10,11}$')))
async def set_phone_number_warning(message: Message):
    await message.answer(
        'Телефон должен быть в виде текста\n'
        'А также должно быть мин. 10 цифр и макс. 11'
    )



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
    _, _, _, date_, hour, minute = callback.data.split(':')
    date_obj = datetime.strptime(date_, '%d.%m.%Y').date()
    formatted_time: str = str(time(hour=int(hour), minute=int(minute)).strftime('%H:%M'))
    user: UserOut = await BotService.find_user(telegram_id=callback.from_user.id)
    await callback.answer()
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
                        tg_id=client[4] if client[4] else None
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
            if cancel_booking.tg_id:
                await bot.send_message(
                    chat_id=int(cancel_booking.tg_id),
                    text=
                    f'<b>Вам отменили запись</b>\n'
                    f'Дата: <b>{date_}</b>\n'
                    f'Время: <b>{formatted_time}</b>\n'
                    f'Причина: <b>{cancel_booking.description}</b>'
                )


@user_router.message(StateFilter(default_state), CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        'Привет, это Бот от сайта Scheduler\n'
        'Функционал почти такой же как на сайте\n'
        'Можно записываться/смотреть свои записи/отменять\n'
        'Также можно смотреть своих ближайших клиентов и отменять им запись '
        'и получать уведомления\n\n'
        'Чтобы посмотреть все команды - введите /help или нажмите на <b>Menu</b>'
    )
    user: TelegramOut = await BotService.find_user_by_tg_id(telegram_id=message.from_user.id)
    if not user:
        await BotService.add_new_user(telegram_id=message.from_user.id)
    

@user_router.message(StateFilter(default_state), Command('id'))
async def get_my_id(message: Message):
    await message.answer(f'Ваш ID\n\n<b>{message.from_user.id}</b>\n\nВставьте его на сайте при записи')


@user_router.message(StateFilter(default_state), Command('clients'))
async def my_clients(message: Message):
    user: UserOut = await BotService.find_user(telegram_id=message.from_user.id)
    if not user:
        return await message.answer('Вы не привязали свой телеграм к профилю на сайте')
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

@user_router.message(StateFilter(default_state), Command('link'))
async def get_my_personal_link(message: Message):
    user: UserOut = await BotService.find_user(telegram_id=message.from_user.id)
    if not user:
        return await message.answer('Вы не подключили свой телеграм к профилю на сайте')
    await message.answer('Ваша персональная ссылка, скопируйте ее и отправьте клиентам')
    await message.answer(user.personal_link)


@user_router.message(StateFilter(default_state), Command('connect'))
async def connect_telegram(message: Message):
    token: str = await generate_token_connect_tg(str(message.from_user.id))
    inline_kb: InlineKeyboardMarkup = create_inline_button_connect_tg(token=token)
    await message.answer(
        'Нажмите на кнопку чтобы привязать ваш аккаунт',
        reply_markup=inline_kb
    )


@user_router.message(StateFilter(default_state), Command('help'))
async def help_command(message: Message):
    await message.answer(
        '<b>Все доступные команды</b>\n\n'
        '/start  -  Запустить бота\n'
        '/id  -  Получить свой ID\n'
        '/new  -  Сделать запись\n'
        '/link  -  Посмотреть свою персональную ссылку\n'
        '/connect  -  Привязать Телеграм к сайту\n'
        '/clients  -  Посмотреть ближайших клиентов\n'
        '/date  -  Посмотреть забронированное время на определенную дату\n'
        '/cancel  -  Отменить действие'
    )


@user_router.message(StateFilter(default_state))
async def echo(message: Message):
    await message.answer(
        "Это неизвестная команда. Чтобы посмотреть все доступные команды введите /help"
    )