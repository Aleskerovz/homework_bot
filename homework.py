import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

TOKENS_NAME = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']

# Сообщения для функции check_tokens
START_MESSAGE_TOKENS = 'Проверка доступности переменных окружения.'
SUCCESS_MESSAGE_TOKENS = 'Все переменные окружения доступны.'
ERROR_MESSAGE_TOKENS = 'Отсутствует переменная/ые окружения: {0}'

# Сообщения для функции send_message
MESSAGE_SEND_START = 'Отправка сообщения.'
MESSAGE_SEND_SUCCESSFULLY = 'Сообщение: {message} отправлено.'
MESSAGE_SEND_ERROR = 'Не удалось отправить сообщение: {message} -> {error}.'

# Сообщения для функции get_api_answer
API_ANSWER_LOG_INFO = (
    'Начало запроса к {url}, {headers}, c значениями {params}')
ERROR_ANSWER = (
    'Ошибка подключения {url}, {headers}, c значениями {params}, '
    'ошибка: {error}')
FAILED_REQUEST = ('Получен неожиданный статус API - {status}, {url}, '
                  '{headers}, c значениями {params}')

SERVER_FAILURES = (
    'Ошибка сервера: {error} - {value}\n'
    '{url}, {headers}, {params}.'
)

# Сообщения для функции check_response
CHECK_RESPONSE_MESSAGE_START = 'Начало проверки ответа API.'
NOT_DICT = 'В ответе тип {0} не является словарем.'
NOT_FOUND_HOMEWORK = 'В ответе нет значения "homeworks".'
NOT_LIST = 'Тип {} не список.'
CHECK_RESPONSE_MESSAGE_SUCCESS = 'Провекра ответа API закончена.'

# Сообщения для функции parse_status
HOMEWORK_NAME_NOT_IN = 'Ключ "homework_name" отсутвует в ответе.'
UNEXPECTED_STATUS = 'Неожиданный статус проверки {status}'
MESSAGE_REVIEW_STATUS = 'Изменился статус проверки работы "{0}" {1}'

# Сообщения для функции main
BOT_START_MESSAGE = 'Бот запущен.'
EXCEPTION_ERROR_MESSAGE = 'Сбой в работе программы: {error}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logging.info(START_MESSAGE_TOKENS)
    non_exists_variables = [
        name for name in TOKENS_NAME
        if globals()[name] == '' or globals()[name] is None
    ]
    if non_exists_variables:
        logging.critical(ERROR_MESSAGE_TOKENS.format(non_exists_variables))
        raise ValueError(
            ERROR_MESSAGE_TOKENS.format(non_exists_variables))
    logging.info(SUCCESS_MESSAGE_TOKENS)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    logging.info(MESSAGE_SEND_START)
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(MESSAGE_SEND_SUCCESSFULLY.format(message=message))
        return True
    except telegram.error.TelegramError as error:
        logging.exception(
            MESSAGE_SEND_ERROR.format(message=message, error=error))
        return False


def get_api_answer(timestamp):
    """Отправляет GET-запрос к API Practicum."""
    params = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    )
    logging.info(API_ANSWER_LOG_INFO.format(**params))
    try:
        homework = requests.get(**params)
    except requests.exceptions.RequestException as error:
        raise ConnectionError(ERROR_ANSWER.format(error=error, **params))
    if homework.status_code != 200:
        raise RuntimeError(
            FAILED_REQUEST.format(status=homework.status_code, **params))
    homework_json = homework.json()
    for error in ('code', 'error'):
        if error in homework_json:
            raise RuntimeError(SERVER_FAILURES.format(
                error=error,
                value=homework_json[error],
                **params
            ))
    return homework_json


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.debug(CHECK_RESPONSE_MESSAGE_START)
    if not isinstance(response, dict):
        raise TypeError(NOT_DICT.format(type(response).__name__))
    if 'homeworks' not in response:
        raise ValueError(NOT_FOUND_HOMEWORK)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(NOT_LIST.format(type(response).__name__))
    logging.debug(CHECK_RESPONSE_MESSAGE_SUCCESS)
    return homeworks


def parse_status(homework):
    """
    Извлекает из информации о конкретной.
    домашней работе статус этой работы.
    """
    if 'homework_name' not in homework:
        raise TypeError(HOMEWORK_NAME_NOT_IN)
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(UNEXPECTED_STATUS.format(status=status))
    return MESSAGE_REVIEW_STATUS.format(
        homework.get('homework_name'), HOMEWORK_VERDICTS[status])


def main():
    """Основная логика работы бота."""
    logging.info(BOT_START_MESSAGE)
    timestamp = int(time.time())
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    previous_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks and send_message(bot, parse_status(homeworks[0])):
                timestamp = response.get(
                    'current_date', timestamp
                )
        except Exception as error:
            message = EXCEPTION_ERROR_MESSAGE.format(error=error)
            logging.exception(message)
            if previous_message != message and send_message(bot, message):
                previous_message = message
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('bot.log')
        ]
    )
    main()
