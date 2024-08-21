from aiogram.types import KeyboardButton, InlineKeyboardButton, BotCommand, InlineKeyboardMarkup
from aiogram import Bot
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import date, datetime


async def set_main_menu(bot: Bot):

    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота и получить ID'),
        BotCommand(command='/clients',
                   description='Мои ближайшие клиенты'),
        BotCommand(command='/bookings',
                   description='Мои ближайшие записи'),
        BotCommand(command='/help',
                   description='Все команды'),        
        BotCommand(command='/cancel',
                   description='Отменить'),
    ]

    await bot.set_my_commands(main_menu_commands)



def create_inline_button(selected_times: list[str], booking_id: int, user_id: int, date: str) -> InlineKeyboardBuilder:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for item in selected_times:
        builder.add(InlineKeyboardButton(text=item[0], callback_data=f'cancel:{booking_id}:{user_id}:{date}:{item[0]}'))
    builder.adjust(5)
    return builder.as_markup()

def confirmation_markup(booking_id: int, user_id: int, date_: str, hour: str, minute: str) -> InlineKeyboardMarkup:
    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Подтвердить',
                callback_data=f'confirm_cancel:{booking_id}:{user_id}:{date_}:{hour}:{minute}'
            )],
            [InlineKeyboardButton(
                text='Отменить',
                callback_data="action_cancel"
            )]
        ]
    )
    return markup
