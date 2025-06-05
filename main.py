from fastapi import FastAPI, Request, HTTPException
from aiogram import types, Bot, Dispatcher
from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN
import os

app = FastAPI()

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
    info = await bot.get_webhook_info()
    print("📡 getWebhookInfo:", info)

@app.post("/webhook")
async def secure_webhook(request: Request):
    print("🟢 Webhook triggered")

    token = request.query_params.get("token")
    if token != TELEGRAM_BOT_TOKEN:
        print("🔒 Неверный токен в запросе")
        raise HTTPException(status_code=403, detail="Недействительный токен")

    try:
        data = await request.json()
        update = types.Update.model_validate(data)
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await dp.process_update(update)
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
