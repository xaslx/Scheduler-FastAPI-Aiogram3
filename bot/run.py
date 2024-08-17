from json import JSONDecodeError
from config import settings
from fastapi import Response, Request
from aiogram import Bot, Dispatcher, types
from bot.user_handler import user_router
from logger import logger
from bot.keyboards import set_main_menu
from aiogram.client.default import DefaultBotProperties
from bot.admin_handler import admin_router


bot: Bot = Bot(settings.TOKEN_BOT, default=DefaultBotProperties(parse_mode="HTML"))
dp: Dispatcher = Dispatcher()
web_hook: str = f'/{settings.TOKEN_BOT}'


async def set_webhook():
    webhook_url: str = f'{settings.WEBHOOK_URL}{web_hook}'
    await bot.set_webhook(webhook_url)

async def on_startup():
    await set_webhook()
    await set_main_menu(bot)


async def handle_web_hook(request: Request):
    url: str = str(request.url)
    index: str = url.rfind('/')
    token: str = url[index + 1:]
    if token == settings.TOKEN_BOT:
        try:
            request_data = await request.json()
            update = types.Update(**request_data)
            await dp.feed_webhook_update(bot, update)
            return Response()
        except JSONDecodeError:
            logger.error('Ошибка декодирования Json')
    else:
        return Response(status_code=403)

dp.startup.register(on_startup)
dp.include_router(user_router)
dp.include_router(admin_router)
