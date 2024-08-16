from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram import Bot
from config import settings

bot: Bot = Bot(settings.TOKEN_BOT)


async def set_main_menu(bot: Bot):

    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/clients',
                   description='Мои ближайшие клиенты'),
        BotCommand(command='/bookings',
                   description='Мои записи'),
        BotCommand(command='/help',
                   description='Все команды'),        
        BotCommand(command='/cancel',
                   description='Отменить'),
    ]

    await bot.set_my_commands(main_menu_commands)