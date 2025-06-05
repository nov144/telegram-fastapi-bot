from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
import os

# 📌 Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_BASE:
    raise RuntimeError("❌ Переменные окружения BOT_TOKEN и WEBHOOK_URL обязательны!")

WEBHOOK_BASE = WEBHOOK_BASE.rstrip("/")
FULL_WEBHOOK_URL = f"{WEBHOOK_BASE}/webhook?token={BOT_TOKEN}"

# 📦 Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# ✅ Хендлер команды /start
@dp.message(F.text == "/start")
async def handle_start(message: Message):
    print("📥 Получен /start")
    await message.answer("Привет, я бот!")

# 🚀 Запуск
@app.on_event("startup")
async def on_startup():
    print("🚀 Старт приложения")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(FULL_WEBHOOK_URL)
    info = await bot.get_webhook_info()
    print("📡 Webhook info:", info)

@app.post("/webhook")
async def webhook(request: Request):
    print("🟢 Webhook triggered")

    token = request.query_params.get("token")
    if token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="❌ Неверный токен")

    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
        print("✅ Обновление обработано")
    except Exception as e:
        print("❌ Ошибка:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    await bot.session.close()
