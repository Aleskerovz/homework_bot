# Telegram-bot

### Описание:
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум. Раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы. При обновлении статуса анализирует ответ API и отправляет вам соответствующее сообщение в Telegram.

### Технологии
![Python](https://img.shields.io/badge/Python-%23254F72?style=for-the-badge&logo=python&logoColor=yellow&labelColor=254f72)
![Telegram](https://img.shields.io/badge/telegram-28A4E4?style=for-the-badge&logo=telegram&logoColor=white&labelColor=28A4E4)

### Как запустить проект:

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Aleskerovz/homework_bot.git
```
```
cd homework_bot
```
2. Создать файл .env:

PRACTICUM_TOKEN = [токен Яндекс.Практикум](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)  
TELEGRAM_TOKEN = токен вашего бота Telegram полученный от BotFather  
TELEGRAM_CHAT_ID = ID вашего чата в Telegram

3. Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
* Если у вас Linux/macOS
    ```
    source venv/bin/activate
    ```
* Если у вас windows
    ```
    source venv/scripts/activate
    ```
```
python3 -m pip install --upgrade pip
```
4. Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
5. Запустить проект:
```
python3 homework.py
```

### Автор проекта:
[**Алескеров Заур**](https://github.com/Aleskerovz)
