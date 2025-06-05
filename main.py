from fastapi import FastAPI, Request
from aiogram import types, Bot, Dispatcher
from bot import bot, dp
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL

app = FastAPI()
WEBHOOK_PATH = f"/bot/{TELEGRAM_BOT_TOKEN}"
FULL_WEBHOOK_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

@app.on_event("startup")
async def on_startup():
    info = await bot.get_webhook_info()
    if info.url != FULL_WEBHOOK_URL:
        await bot.set_webhook(FULL_WEBHOOK_URL)
        print("✅ Webhook установлен:", FULL_WEBHOOK_URL)

@app.post(WEBHOOK_PATH)
async def receive_update(request: Request):
    update = await request.json()
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()