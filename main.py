from fastapi import FastAPI, Request, HTTPException
from aiogram import types, Bot, Dispatcher, F
from aiogram.types import Message
from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN
import os
import asyncio
import httpx  # для пинга

app = FastAPI()

# ✅ Хендлер команды /start
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
    print("🚀 Старт приложения")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(FULL_WEBHOOK_URL)
    print("✅ Webhook установлен:", FULL_WEBHOOK_URL)

    # 🟢 Запускаем фоновые пинги, чтобы Render не завершал процесс
    asyncio.create_task(ping_forever())

async def ping_forever():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{WEBHOOK_BASE}/health")
                print("📡 ping /health:", resp.status_code)
        except Exception as e:
            print("❌ ping error:", e)
        await asyncio.sleep(60)

@app.post("/webhook")
async def webhook(request: Request):
    token = request.query_params.get("token")
    if token != TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Недействительный токен")

    try:
        data = await request.json()
        update = types.Update.model_validate(data)
        await dp.feed_update(bot, update)
        print("✅ Обновление обработано")
    except Exception as e:
        print("❌ Ошибка при обработке webhook:", e)

    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

