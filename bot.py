import logging
import os
import asyncio
import functools
import html
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import MessageEntityType

# Импортируем нашу функцию скачивания
from downloader import download_video

# Загружаем переменные окружения из файла .env
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен вашего бота теперь берется из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Указываем путь к файлу с cookie
COOKIES_FILE = "youtube-cookies.txt"


async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Скачивает видео по ссылке и отправляет его в чат."""
    message = update.message
    if not message or not message.text:
        return

    # Извлекаем первую ссылку из сообщения
    url_entities = [e for e in message.entities if e.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK)]
    if not url_entities:
        return  # Не должно произойти из-за фильтров

    entity = url_entities[0]
    if entity.type == MessageEntityType.URL:
        url = message.text[entity.offset : entity.offset + entity.length]
    else:  # TEXT_LINK
        url = entity.url

    if not url:
        return

    # Проверяем наличие файла с cookie
    if not os.path.exists(COOKIES_FILE):
        await message.reply_text(
            f"Ошибка: Файл с cookie не найден.\n"
            f"Убедитесь, что файл '{COOKIES_FILE}' находится в той же папке, что и бот."
        )
        return

    status_message = await message.reply_text("Получил ссылку. Начинаю скачивание... ⏳")

    try:
        # Запускаем блокирующую функцию скачивания в отдельном потоке
        loop = asyncio.get_running_loop()
        download_task = functools.partial(download_video, url=url, cookies_file=COOKIES_FILE)
        video_path, video_title = await loop.run_in_executor(None, download_task)

        if video_path and os.path.exists(video_path):
            await status_message.edit_text("Видео скачано! Отправляю... 🚀")
            
            # Экранируем специальные HTML-символы в названии и делаем его жирным
            escaped_title = html.escape(video_title)
            caption_html = f"<b>{escaped_title}</b>"

            # Отправляем видео, увеличив тайм-ауты и добавив жирную подпись
            with open(video_path, 'rb') as video_file:
                await message.reply_video(
                    video=video_file, 
                    caption=caption_html,
                    parse_mode='HTML', # Указываем, что используем HTML-разметку
                    supports_streaming=True,
                    read_timeout=60,
                    write_timeout=60
                )
            
            # Удаляем сообщение о статусе
            await status_message.delete()
        else:
            await status_message.edit_text("Не удалось скачать видео. 😞")

    except Exception as e:
        logger.error(f"Ошибка при обработке ссылки {url}: {e}", exc_info=True)
        await status_message.edit_text("Произошла непредвиденная ошибка. 🤯")
    finally:
        # Удаляем файл после отправки или в случае ошибки
        if 'video_path' in locals() and video_path and os.path.exists(video_path):
            os.remove(video_path)
            logger.info(f"Удалил временный файл: {video_path}")


def main() -> None:
    """Запуск бота."""
    # Проверяем, что токен был загружен
    if not TOKEN:
        logger.critical("Переменная окружения TELEGRAM_BOT_TOKEN не найдена!")
        logger.critical("Создайте файл .env и добавьте в него строку: TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН")
        return

    application = Application.builder().token(TOKEN).build()

    # Фильтр для ссылок
    link_filters = filters.Entity(MessageEntityType.URL) | filters.Entity(MessageEntityType.TEXT_LINK)
    application.add_handler(MessageHandler(link_filters, link_handler))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main() 