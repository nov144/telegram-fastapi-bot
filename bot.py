from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

from aiogram import types
from aiogram.filters import Command

@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer("Привет!")