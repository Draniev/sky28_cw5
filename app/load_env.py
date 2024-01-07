import os
from dotenv import load_dotenv

is_load = load_dotenv()
if not is_load:
    print('Загрузить переменные среды не вышло!')
    raise FileNotFoundError

SJ_API_KEY = os.getenv('SJ_API_KEY')
if SJ_API_KEY is None:
    print('Загрузить АПИ ключ не вышло!')
    SJ_API_KEY = 'test'
    raise ValueError('Загрузить АПИ ключ не вышло!')
