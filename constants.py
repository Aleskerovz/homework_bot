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

PREVIOUS_TIMESTAMP = 60
