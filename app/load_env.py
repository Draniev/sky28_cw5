import os

from dotenv import load_dotenv

from app.service.db_manager import DBManager

is_load = load_dotenv()
if not is_load:
    print('Загрузить переменные среды не вышло!')
    raise FileNotFoundError

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

if (DB_NAME or DB_PASS or DB_USER) is None:
    print('Загрузить АПИ ключ не вышло!')
    raise ValueError('Загрузить АПИ ключ не вышло!')

db_params = {
    'host': 'localhost',
    'dbname': DB_NAME,
    'password': DB_PASS,
    'user': DB_USER,
    'port': 5432,
}

db = DBManager(**db_params)
