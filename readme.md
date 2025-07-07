## Использует [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## 🚀 Установка

### 1. Клонирйте репозиторий

```bash
git clone https://github.com/veomall/group-dlp_bot.git
```

### 2. Настройте окружение

```bash
python -m venv .venv
# Для Windows
.venv\Scripts\activate
# Для macOS/Linux
source .venv/bin/activate
```

Создайте в корневой папке проекта файл с названием `.env`.
Откройте этот файл и добавьте в него следующую строку, заменив `YOUR_BOT_TOKEN` на реальный токен, который вы получили от [**@BotFather**](https://t.me/BotFather):
```
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

### 3. Установите зависимости

Выполните в терминале следующую команду:
```bash
pip install -r requirements.txt
```

### 4. Настройте приватность бота

Чтобы бот мог видеть все сообщения в группе, а не только команды, нужно отключить режим приватности.
1. Отправьте команду `/mybots` боту [**@BotFather**](https://t.me/BotFather).
2. Выберите вашего бота из списка.
3. Перейдите в **Bot Settings** -> **Group Privacy**.
4. Нажмите кнопку **Turn off**.

### 5. Экспортируйте cookie-файлы

Для скачивания видео с YouTube (и некоторых других сайтов) боту нужны cookie-файлы из вашего браузера.

1. Установите расширение для вашего браузера. Рекомендуется **"Get cookies.txt LOCALLY"**:
   - [Для Google Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - [Для Mozilla Firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)
2. Откройте в браузере сайт **youtube.com**.
3. Нажмите на иконку установленного расширения и экспортируйте cookie, нажав на кнопку **"Export"**.
4. Сохраните файл под именем `youtube-cookies.txt` в ту же папку, где лежат остальные файлы проекта.

## ▶️ Запуск

```bash
python bot.py
```

Теперь вы можете добавить бота в любой групповой чат, и он будет готов к работе. Просто отправьте ссылку на видео, и он сделает все остальное!
