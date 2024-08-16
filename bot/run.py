from config import settings
from aiogram.types import Message
from aiogram.filters import CommandStart
from fastapi import Response, Request
from aiogram import Bot, Dispatcher, types




bot: Bot = Bot(settings.TOKEN_BOT)
dp: Dispatcher = Dispatcher()
web_hook: str = f'/{settings.TOKEN_BOT}'


async def set_webhook():
    webhook_url = f'{settings.WEBHOOK_URL}{web_hook}'
    await bot.set_webhook(webhook_url)

async def on_startup():
    await set_webhook()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('hello')

async def handle_web_hook(request: Request):
    url = str(request.url)
    index = url.rfind('/')
    token = url[index + 1:]
    if token == settings.TOKEN_BOT:
        request_data = await request.json()
        update = types.Update(**request_data)
        await dp.feed_webhook_update(bot, update)
        return Response()
    else:
        return Response(status_code=403)

dp.startup.register(on_startup)