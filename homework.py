import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import constants

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


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logging.info(constants.START_MESSAGE_TOKENS)
    if all([globals()[name] for name in constants.TOKENS_NAME]):
        logging.info(constants.SUCCESS_MESSAGE_TOKENS)
        return True
    else:
        non_exists_variables = [
            name for name in constants.TOKENS_NAME if not globals()[name]]
        logging.critical(
            constants.ERROR_MESSAGE_TOKENS.format(non_exists_variables))
        sys.exit(1)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    logging.info(constants.MESSAGE_SEND_START)
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(
            constants.MESSAGE_SEND_SUCCESSFULLY.format(message=message))
        return True
    except telegram.error.TelegramError as error:
        logging.exception(
            constants.MESSAGE_SEND_ERROR.format(message=message, error=error))
        return False


def get_api_answer(timestamp):
    """Отправляет GET-запрос к API Practicum."""
    params = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={'from_date': timestamp}
    )
    logging.info(constants.API_ANSWER_LOG_INFO.format(**params))
    try:
        homework = requests.get(**params)
    except requests.exceptions.RequestException as error:
        raise ConnectionError(
            constants.ERROR_ANSWER.format(error=error, **params))
    if homework.status_code != HTTPStatus.OK:
        raise RuntimeError(
            constants.FAILED_REQUEST.format(
                status=homework.status_code, **params))
    try:
        homework_json = homework.json()
    except json.JSONDecodeError as error:
        raise RuntimeError(
            constants.ERROR_ANSWER.format(error=error, **params))
    for error in ('code', 'error'):
        if error in homework_json:
            raise RuntimeError(constants.SERVER_FAILURES.format(
                error=error,
                value=homework_json[error],
                **params
            ))
    return homework_json


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.debug(constants.CHECK_RESPONSE_MESSAGE_START)
    if not isinstance(response, dict):
        raise TypeError(constants.NOT_DICT.format(type(response).__name__))
    if 'homeworks' not in response:
        raise ValueError(constants.NOT_FOUND_HOMEWORK)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(constants.NOT_LIST.format(type(response).__name__))
    logging.debug(constants.CHECK_RESPONSE_MESSAGE_SUCCESS)
    return homeworks


def parse_status(homework):
    """
    Извлекает из информации о конкретной.
    домашней работе статус этой работы.
    """
    if 'homework_name' not in homework:
        raise TypeError(constants.HOMEWORK_NAME_NOT_IN)
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(constants.UNEXPECTED_STATUS.format(status=status))
    return constants.MESSAGE_REVIEW_STATUS.format(
        homework.get('homework_name'), HOMEWORK_VERDICTS[status])


def main():
    """Основная логика работы бота."""
    logging.info(constants.BOT_START_MESSAGE)
    timestamp = int(time.time()) - constants.PREVIOUS_TIMESTAMP
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
            message = constants.EXCEPTION_ERROR_MESSAGE.format(error=error)
            logging.exception(message)
            if previous_message != message and send_message(bot, message):
                previous_message = message
            elif previous_message == message:
                previous_message = ''
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
