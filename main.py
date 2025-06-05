from fastapi import FastAPI, Request, HTTPException
from aiogram import types, Bot, Dispatcher, F
from aiogram.types import Message
from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN
import os

app = FastAPI()

# ✅ Команда /start
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    print("📥 Получен /start")
    await message.answer("Привет, я бот!")

# 🌍 Получаем URL из Render ENV
WEBHOOK_BASE = os.getenv("WEBHOOK_URL")
if not WEBHOOK_BASE:
    raise RuntimeError("❌ WEBHOOK_URL не задан!")

WEBHOOK_BASE = WEBHOOK_BASE.rstrip("/")
FULL_WEBHOOK_URL = f"{WEBHOOK_BASE}/webhook?token={TELEGRAM_BOT_TOKEN}"
print("➡️ FULL_WEBHOOK_URL:", FULL_WEBHOOK_URL)

@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(FULL_WEBHOOK_URL)
    print("✅ Webhook установлен:", FULL_WEBHOOK_URL)

@app.post("/webhook")
async def webhook(request: Request):
    token = request.query_params.get("token")
    if token != TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Недействительный токен")
    data = await request.json()
    update = types.Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
