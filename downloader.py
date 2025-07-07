import yt_dlp
import os
import argparse

def download_video(url, cookies_file=None, output_path='downloads'):
    """
    Скачивает видео по заданному URL с помощью yt-dlp и возвращает путь к файлу и его название.

    :param url: URL видео для скачивания.
    :param cookies_file: Путь к файлу с cookies.
    :param output_path: Папка для сохранения скачанного видео.
    :return: Кортеж (путь к файлу, название) или (None, None) в случае ошибки.
    """
    # Создаем папку для загрузок, если она не существует
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Настройки для yt-dlp
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'best',
        'cookiefile': cookies_file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Начинаю скачивание видео с: {url}")
            # Скачиваем и получаем информацию о видео
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Без названия')
            
            # yt-dlp 2023.11.16+ сохраняет путь в 'requested_downloads'
            if 'requested_downloads' in info and info['requested_downloads']:
                 downloaded_file_path = info['requested_downloads'][0]['filepath']
            else:
                # Для более старых версий или других случаев
                 downloaded_file_path = ydl.prepare_filename(info)

            print(f"Скачивание завершено! Файл сохранен как: {downloaded_file_path}")
            return downloaded_file_path, video_title
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Скачивание видео с помощью yt-dlp.",
        formatter_class=argparse.RawTextHelpFormatter # для красивого вывода help
    )
    
    parser.add_argument("url", help="URL видео для скачивания.")
    
    # Группа для взаимоисключающих аргументов
    cookie_group = parser.add_mutually_exclusive_group()
    cookie_group.add_argument(
        "-c", "--cookies", 
        help="Путь к файлу cookies в формате Netscape (cookies.txt)."
    )

    parser.add_argument(
        "-o", "--output", 
        default="downloads", 
        help="Папка для сохранения видео (по умолчанию: 'downloads')."
    )

    args = parser.parse_args()

    # Проверяем, существует ли файл с cookie, если он указан
    if args.cookies and not os.path.exists(args.cookies):
        print(f"Ошибка: Файл с cookie не найден по пути: {args.cookies}")
        exit(1)

    downloaded_file, title = download_video(
        url=args.url, 
        cookies_file=args.cookies, 
        output_path=args.output
    )

    if downloaded_file:
        print(f"\nВидео '{title}' успешно скачано: {downloaded_file}")
    else:
        print("\nНе удалось скачать видео.")
