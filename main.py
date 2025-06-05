from fastapi import FastAPI, Request
from aiogram import types, Bot, Dispatcher
from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN
from urllib.parse import quote
import os

app = FastAPI()

# Получаем переменные окружения
WEBHOOK_BASE = os.getenv("WEBHOOK_URL")
if not WEBHOOK_BASE:
    raise RuntimeError("❌ Переменная окружения WEBHOOK_URL не задана!")

WEBHOOK_BASE = WEBHOOK_BASE.rstrip("/")
TOKEN_SAFE = quote(TELEGRAM_BOT_TOKEN, safe="")
WEBHOOK_PATH = f"/bot/{TOKEN_SAFE}"
FULL_WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"

print("➡️ FULL_WEBHOOK_URL:", FULL_WEBHOOK_URL)

@app.on_event("startup")
async def on_startup():
    info = await bot.get_webhook_info()
    if info.url != FULL_WEBHOOK_URL:
        await bot.set_webhook(FULL_WEBHOOK_URL)
        print("✅ Webhook установлен:", FULL_WEBHOOK_URL)

# 🔐 Жёстко заданный маршрут, совпадающий с тем, что Telegram реально вызывает
@app.post("/bot/7533256493%3AAAGEVcz3mj3kN02B1mucgYtcrzg5eAR1Y1I")
async def receive_update(request: Request):
    data = await request.json()
    update = types.Update.model_validate(data)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
