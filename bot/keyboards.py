from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram import Bot

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