import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import yt_dlp
import aiofiles

# ==== НАСТРОЙКИ ====
TOKEN = '7937530249:AAFSa7utF67UhEPtKwA_EYdC2cK6OrHSL1Y'  # ЗАМЕНИ!

bot = Bot(token=TOKEN)
dp = Dispatcher()

class InstantMusicBot:
    def __init__(self):
        # САМЫЕ БЫСТРЫЕ НАСТРОЙКИ НА СВЕТЕ
        self.download_opts = {
            # Берём готовое аудио, НЕ конвертируем
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': 'temp/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'socket_timeout': 10,
            'retries': 2,
            'fragment_retries': 1,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'extractaudio': True,
            'audioformat': 'm4a',  # m4a уже готовое аудио
            'postprocessors': [],  # НИКАКОЙ конвертации!
            'concurrent_fragment_downloads': 8,  # 8 потоков!
            'http_chunk_size': 20971520,  # 20MB чанки
            'buffersize': 4194304,  # 4MB буфер
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],  # Быстрый клиент
                    'skip': ['hls', 'dash'],  # Пропускаем медленные форматы
                }
            },
            'throttledratelimit': 0,  # Без ограничений скорости
        }
    
    async def search_fast(self, query: str):
        """Мгновенный поиск"""
        search_opts = {
            'quiet': True,
            'extract_flat': True,
            'default_search': 'ytsearch5:',
            'no_warnings': True,
            'socket_timeout': 5,
        }
        
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                
                results = []
                for entry in info.get('entries', []):
                    if entry:
                        title = entry.get('title', 'Трек')[:50]
                        # Убираем мусор из названия
                        title = re.sub(r'\[.*?\]|\(.*?\)', '', title)
                        title = ' '.join(title.split())
                        
                        results.append({
                            'id': entry.get('id'),
                            'title': title,
                            'url': f"https://youtu.be/{entry.get('id')}",
                            'duration': entry.get('duration', 0),
                        })
                
                return results
        except:
            return []
    
    async def download_instant(self, video_id: str, title: str):
        """Скачивает за 10-30 секунд"""
        try:
            # Удаляем старые файлы
            for file in os.listdir('temp'):
                if file.startswith(video_id):
                    os.remove(f'temp/{file}')
            
            # Скачиваем
            with yt_dlp.YoutubeDL(self.download_opts) as ydl:
                ydl.download([f"https://youtu.be/{video_id}"])
            
            # Ищем скачанный файл
            for file in os.listdir('temp'):
                if file.startswith(video_id):
                    filepath = f'temp/{file}'
                    
                    # Проверяем размер (должен быть > 100KB)
                    if os.path.getsize(filepath) > 100000:
                        return filepath
            
            return None
            
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
            return None

# Инициализация
bot_engine = InstantMusicBot()

# Словарь для хранения поисков
user_data = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚡ <b>Мгновенный музыкальный бот</b>\n\n"
        "Просто напиши название песни!\n"
        "Скачивание за <b>10-30 секунд</b> ⚡\n\n"
        "<i>Пример: Billie Eilish, The Weeknd, реп</i>",
        parse_mode=ParseMode.HTML
    )

@dp.message()
async def search_music(message: types.Message):
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer("❌ Напиши название подлиннее")
        return
    
    # Быстрый поиск
    msg = await message.answer(f"🔍 <b>Ищу:</b> {query}...")
    
    tracks = await bot_engine.search_fast(query)
    
    if not tracks:
        await msg.edit_text(f"❌ Ничего не найдено: {query}")
        return
    
    # Сохраняем для пользователя
    user_data[message.from_user.id] = tracks
    
    # Создаём кнопки
    keyboard = []
    for i, track in enumerate(tracks[:5]):  # Максимум 5
        btn_text = f"🎵 {i+1}. {track['title']}"
        if len(btn_text) > 40:
            btn_text = btn_text[:37] + "..."
        
        keyboard.append([
            types.InlineKeyboardButton(
                text=btn_text,
                callback_data=f"dl_{i}"
            )
        ])
    
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await msg.edit_text(
        f"✅ <b>Найдено {len(tracks)} треков:</b>\n\n"
        f"<i>Выбери номер для мгновенного скачивания ⚡</i>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(lambda c: c.data.startswith("dl_"))
async def download_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_data:
        await callback.answer("❌ Начни поиск заново")
        return
    
    tracks = user_data[user_id]
    track_idx = int(callback.data.split('_')[1])
    
    if track_idx >= len(tracks):
        await callback.answer("❌ Ошибка")
        return
    
    track = tracks[track_idx]
    
    await callback.answer(f"⚡ Скачиваю: {track['title'][:20]}...")
    
    # Статус
    status_msg = await callback.message.answer(
        f"⚡ <b>Мгновенное скачивание...</b>\n"
        f"<i>Трек:</i> {track['title']}\n"
        f"<i>Ожидание:</i> 10-30 сек",
        parse_mode=ParseMode.HTML
    )
    
    # СКАЧИВАЕМ
    try:
        filepath = await bot_engine.download_instant(track['id'], track['title'])
        
        if filepath and os.path.exists(filepath):
            # ОТПРАВЛЯЕМ КАК АУДИОФАЙЛ
            async with aiofiles.open(filepath, 'rb') as audio_file:
                await bot.send_audio(
                    chat_id=user_id,
                    audio=types.BufferedInputFile(
                        await audio_file.read(),
                        filename=f"{track['title'][:30]}.m4a"
                    ),
                    caption=f"🎵 {track['title']}\n⚡ <b>Скачано мгновенно!</b>",
                    parse_mode=ParseMode.HTML
                )
            
            # Удаляем файл
            os.remove(filepath)
            
            await status_msg.edit_text(f"✅ <b>Готово!</b> Трек отправлен")
            
        else:
            await status_msg.edit_text("❌ Не удалось скачать, попробуй другой трек")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")
        print(f"Ошибка: {e}")

# Запуск
async def main():
    # Создаём папку temp
    os.makedirs('temp', exist_ok=True)
    
    print("""
    ⚡⚡⚡ МГНОВЕННЫЙ МУЗЫКАЛЬНЫЙ БОТ ⚡⚡⚡
    
    Запущен! Особенности:
    • Скачивание за 10-30 секунд
    • Без конвертации (m4a)
    • Многопоточная загрузка
    • Автоочистка файлов
    
    Открой Telegram и пиши названия песен!
    """)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())