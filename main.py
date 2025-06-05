from fastapi import FastAPI, Request, HTTPException
from aiogram import types, Bot, Dispatcher, F
from aiogram.types import Message
from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN
import os

app = FastAPI()

# ✅ Хендлер команды /start
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    print("📥 Получен /start")
    await message.answer("Привет, я бот!")

# 📡 Получаем URL из переменных окружения
WEBHOOK_BASE = os.getenv("WEBHOOK_URL")
if not WEBHOOK_BASE:
    raise RuntimeError("❌ WEBHOOK_URL не задан!")

WEBHOOK_BASE = WEBHOOK_BASE.rstrip("/")
FULL_WEBHOOK_URL = f"{WEBHOOK_BASE}/webhook?token={TELEGRAM_BOT_TOKEN}"
print("➡️ FULL_WEBHOOK_URL:", FULL_WEBHOOK_URL)

@app.on_event("startup")
async def on_startup():
    print("🚀 Запуск бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(FULL_WEBHOOK_URL, drop_pending_updates=True)

    info = await bot.get_webhook_info()
    print("📡 Webhook info:", info)

    if info.url != FULL_WEBHOOK_URL:
        print("⚠️ Webhook URL отличается от ожидаемого!")
    else:
        print("✅ Надёжный Webhook установлен")

@app.post("/webhook")
async def secure_webhook(request: Request):
    print("🟢 Webhook triggered")

    token = request.query_params.get("token")
    if token != TELEGRAM_BOT_TOKEN:
        print("🔒 Неверный токен")
        raise HTTPException(status_code=403, detail="Недействительный токен")

    try:
        data = await request.json()
        update = types.Update.model_validate(data)
        await dp.feed_update(bot, update)
        print("✅ Update обработан")
    except Exception as e:
        print("❌ Ошибка при обработке webhook:", str(e))

    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    await bot.session.close()
