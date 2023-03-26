import os.path
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR.resolve().joinpath('secrets')
CONFIG_DIR = BASE_DIR.resolve().joinpath('config')


# DB service settings

#: Файл с параметрами для доступа к базе данных (БД)
DB_SETTINGS_FILE = 'db.json'
DB_SETTINGS_FILE_PATH = SECRETS_DIR.joinpath(DB_SETTINGS_FILE)

if not DB_SETTINGS_FILE_PATH.exists():
    print(f'DB_FILE_PATH: file not found in {os.path.basename(SECRETS_DIR)} directory')
    exit(1)

with open(DB_SETTINGS_FILE_PATH, 'r', encoding='utf-8') as config:
    db_config: dict = json.load(config)

try:
    DB_NAME = db_config['DB_NAME'],
    DB_USER = db_config['DB_USER'],
    DB_PASSWORD = db_config['DB_PASSWORD'],
    DB_HOST = db_config['DB_HOST'],
except Exception as error:
    print('DB: config file structure error', error)
    exit(1)

#: Имя таблицы в базе данных для хранения данных из облака (из GSheet-таблицы)
TABLE_NAME = 'Orders'
#: Количество строк для сдвига при считывании данных из GSheet-таблицы
ROWS_SHIFT = 1
#: Порядок полей в таблице БД
TABLE_FIELDS_ORDER = (
  'table_row_index',
  'table_row_number',
  'order_number',
  'price_usd',
  'price_rub',
  'delivery_date',
)
#: Соответствие поле-индекс
TABLE_FIELDS_INDEX = {
  'table_row_index': 5,
  'table_row_number': 0,
  'order_number': 1,
  'price_usd': 2,
  'price_rub': 4,
  'delivery_date': 3,
}
#: Соответствие поле-тип данных
TABLE_FIELDS_TYPE = {
  "table_row_index": '',
  "table_row_number": '',
  "order_number": '',
  "price_usd": '::NUMERIC(12, 2)',
  "price_rub": '::NUMERIC(12, 2)',
  "delivery_date": '::CHAR(10)',
}


# Google Sheets service settings

API_KEY = 'YourS_Api_kEy'
CREDENTIALS_FILE = 'token.json'
CREDENTIALS_FILE_PATH = SECRETS_DIR.joinpath(CREDENTIALS_FILE)

if not CREDENTIALS_FILE_PATH.exists():
    print(f'CREDENTIALS_FILE: file not found in {os.path.basename(SECRETS_DIR)} directory')
    exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

#: Таблица-источник
SOURCE_SPREADSHEET_ID = '1f-qZEX1k_3nj5cahOzntYAnvO4ignbyesVO7yuBdv_g'
#: Файл сохранения статуса последней проверки GSheet-таблицы
STATE_FILE = 'state_sheets.json'
#: Еmail-адреса, которым будет открыт доступ на редактирование GSheet-таблицы
EMAIL_ADDRESSES = [
    'amkolotov@gmail.com',
]
#: Название листа, на который будут скопированы данные из таблицы-источника
NEW_SHEET_NAME = 'New sheet'

# CBR service settings

VALUTE_CHAR_CODE = 'USD'
VALUTE_INFO_OPEN_TAG = '<CharCode>'
VALUTE_INFO_VALUE_OPEN_TAG = '<Value>'
VALUTE_INFO_VALUE_CLOSE_TAG = '</Value>'
VALUTE_INFO_NOMINAL_OPEN_TAG = '<Nominal>'
VALUTE_INFO_NOMINAL_CLOSE_TAG = '</Nominal>'


# Polling settings

#: Интервал проверки GSheet-таблицы на наличие изменений (минуты)
GS_POLLING_INTERVAL = 10
#: Интервал проверки курса USD (часы)
CBR_POLLING_INTERVAL = 1
