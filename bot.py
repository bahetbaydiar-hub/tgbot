import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из Koyeb Environment variables
TOKEN = os.getenv("TOKEN")

# Проверка токена
if not TOKEN:
    logger.error("❌ ОШИБКА: TOKEN не найден!")
    logger.error("ℹ️  Добавь в Koyeb Environment variables:")
    logger.error("    Key: TOKEN")
    logger.error("    Value: твой_токен_от_BotFather")
    exit(1)

# Инициализация бота с новым синтаксисом
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # ← Новый синтаксис!
)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "✅ <b>Бот работает на Koyeb!</b>\n\n"
        "Токен получен успешно!"
    )

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Вы написали: <code>{message.text}</code>")

async def main():
    logger.info("=" * 50)
    logger.info("🚀 БОТ ЗАПУЩЕН НА KOYEB")
    logger.info(f"✅ Токен: Установлен")
    logger.info("=" * 50)
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
