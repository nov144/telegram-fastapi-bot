# Telegram FastAPI Webhook Bot

## 🚀 Установка и запуск

### Переменные окружения:

- `BOT_TOKEN` — токен Telegram-бота
- `WEBHOOK_URL` — базовый адрес (например, https://your-app.onrender.com)

### Запуск локально:
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Deploy на Render:
- Create Web Service
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`