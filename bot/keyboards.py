from aiogram.types import KeyboardButton, InlineKeyboardButton, BotCommand
from aiogram import Bot
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

async def set_main_menu(bot: Bot):

    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
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



async def create_inline_button(selected_times: list[str]):
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for item in selected_times:
        builder.add(InlineKeyboardButton(text=item[0], url='https://t.me#'))
    builder.adjust(6)
    return builder.as_markup(resize_keyboard=True)