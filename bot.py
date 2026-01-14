import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из переменных окружения Koyeb
TOKEN = os.getenv("7937530249:AAFSa7utF67UhEPtKwA_EYdC2cK6OrHSL1Y")
if not TOKEN:
    logger.error("❌ TOKEN не найден!")
    exit(1)

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚡ <b>Музыкальный бот</b>\n\n"
        "Работает на <b>Koyeb Cloud</b> 24/7!\n\n"
        "Просто напиши название песни...",
    )

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    await message.answer("✅ Бот работает! Хостинг: Koyeb")

@dp.message()
async def search_music(message: types.Message):
    await message.answer(f"🔍 Поиск (функция скоро добавится): {message.text}")

async def main():
    logger.info("🚀 Запускаю бота на Koyeb...")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())

