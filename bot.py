import asyncio
import logging
import os
import re
from typing import Tuple
from uuid import uuid4

import yt_dlp
from dotenv import load_dotenv
from telegram import Update
# Импортируем класс ошибки Telegram для более точного отлова
from telegram.error import TelegramError
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Включаем логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env файла
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Необходимо указать TELEGRAM_TOKEN в .env файле")

# Папка для временного хранения видео
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Ограничение размера файла в байтах (50 МБ - стандартное ограничение Telegram)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Паттерн для поиска URL в тексте
URL_PATTERN = r'https?://[^\s]+'


async def download_video(url: str) -> Tuple[str, str] | None:
    """
    Скачивает видео по URL с помощью yt-dlp.
    Возвращает кортеж (путь к файлу, название видео) или None в случае ошибки.
    """
    temp_filename = os.path.join(DOWNLOAD_DIR, f"{uuid4()}")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{temp_filename}.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'filesize_approx': MAX_FILE_SIZE,
    }

    try:
        def ydl_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                filesize = info.get('filesize') or info.get('filesize_approx')
                if filesize and filesize > MAX_FILE_SIZE:
                    logger.warning(f"Файл слишком большой: {filesize / 1024 / 1024:.2f} MB. URL: {url}")
                    filepath_to_delete = ydl.prepare_filename(info)
                    if os.path.exists(filepath_to_delete):
                         os.remove(filepath_to_delete)
                    return None
                
                filepath = ydl.prepare_filename(info)
                title = info.get('title', 'Видео без названия')
                return filepath, title

        result = await asyncio.to_thread(ydl_download)
        return result

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Ошибка скачивания yt-dlp для URL {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при скачивании {url}: {e}")
        return None


async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик сообщений, который ищет URL, скачивает видео и отправляет его.
    """
    if not update.message or not update.message.text:
        return

    message_text = update.message.text
    match = re.search(URL_PATTERN, message_text)
    
    if not match:
        return
        
    url = match.group(0)
    logger.info(f"Обнаружен URL: {url} в чате {update.effective_chat.id}")

    filepath = None
    try:
        download_result = await download_video(url)
        
        # Сценарий 1: Видео успешно скачано
        if download_result:
            filepath, video_title = download_result
            logger.info(f"Видео '{video_title}' скачано: {filepath}. Попытка отправки...")
            try:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=open(filepath, 'rb'),
                    caption=video_title,
                    reply_to_message_id=update.message.message_id
                )
                logger.info(f"Видео успешно отправлено в чат {update.effective_chat.id}")
            except TelegramError as e:
                # Сценарий 2: Ошибка при отправке в Telegram
                logger.error(f"Ошибка отправки видео в чат {update.effective_chat.id}: {e}")
                await update.message.reply_text(f"Ошибка: {e}")
        # Сценарий 3: Ошибка при скачивании (download_result is None)
        else:
            logger.info(f"Не удалось обработать URL {url}. Сообщение проигнорировано.")

    except Exception as e:
        logger.error(f"Критическая ошибка в обработчике для URL {url}: {e}")
    finally:
        # В любом случае удаляем временный файл, если он был создан
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Временный файл {filepath} удален.")


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, url_handler))
    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()