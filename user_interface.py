from enum import Enum

from rich import print

from hh_vacancyapi import HHVacancyAPI
from load_env import SJ_API_KEY
from sj_vacancyapi import SJVacancyAPI
from vacancy import Vacancy
from vacancyapi import VacancyApi


class UIState(Enum):
    IDLE = 'Ожидаем начала работы'
    LOAD_FILE = 'Ожидаем загрузку вакансий из файла'
    API_SEARCH0 = 'Выбираем сайт для поиска вакансий по АПИ'
    API_SEARCH1 = 'Загружаем критерии поиска вакансий'
    VACANCY = 'Режим работы с загруженными вакансиями'
    EXIT = 'Выключаемся'


class UserInterface:

    def __init__(self):
        self.__state = UIState.IDLE
        self.hh_api = HHVacancyAPI()
        self.sj_api = SJVacancyAPI(SJ_API_KEY)
        self.apies: list[VacancyApi] = []
        self.vacancies: list[Vacancy] = []

    def start(self):
        is_exit = False

        while not is_exit:
            is_exit = self.__hello_ui()

        print('Досвидули, я закрываюсь')

    def __hello_ui(self) -> bool:

        match self.__state:

            case UIState.IDLE:
                print('(1) Поработать с локальными файлами '
                      '\n(2) найти новые вакансии, '
                      '\n(9, exit) выйти?')
                user_input = input('Выберите действие: 1, 2 или 9 >> ')
                is_exit = self.__parse_idle_input(user_input)

            case UIState.LOAD_FILE:
                is_exit = True

            case UIState.API_SEARCH0:
                print('Хотите поискать \n(0) на всех доступных платформах,'
                      '\n(1) на HeadHunter '
                      '\n(2) на SuperJob, '
                      '\n(8, back) назад или выйти (9, exit)?')
                user_input = input('Выберите действие: 0, 1, 2 или 8, 9 >> ')
                is_exit = self.__parse_search0_input(user_input)
                # is_exit = True

            case UIState.API_SEARCH1:
                is_exit = self.__find_vacancy_ui()

            case UIState.VACANCY:
                is_exit = self.__working_with_vacancy()

        print(self.__state)
        print(f'is_exit: {is_exit}')
        return is_exit

    def __parse_idle_input(self, input: str) -> bool:

        match input:
            case '1':
                self.__state = UIState.LOAD_FILE
            case '2':
                self.__state = UIState.API_SEARCH0
            case '9' | 'exit':
                return True  # Завершение и выход

        return False

    def __parse_search0_input(self, input: str) -> bool:

        match input:
            case '0':  # Поиск на ХХ
                self.apies = [self.hh_api]
            case '1':  # Поиск на SJ
                self.apies = [self.sj_api]
            case '2':  # Поиск на обоих платформах
                self.apies = [self.hh_api, self.sj_api]
            case '8' | 'back':  # Возврат на предыдуший шаг
                self.__state = UIState.IDLE
                return False
            case '9' | 'exit':
                return True  # Завершение и выход

        self.__state = UIState.API_SEARCH1
        return False

    def __find_vacancy_ui(self) -> bool:

        keyword = input('(8, back) назад или выйти (9, exit)\n'
                        'Ключевое слово для поиска: ')

        match keyword:
            case '8' | 'back':  # Возврат на предыдуший шаг
                self.__state = UIState.API_SEARCH0
                return False
            case '9' | 'exit':
                return True  # Завершение и выход

        salary = input('(8, back) назад или выйти (9, exit)\n'
                       'Примерная зарплата в RUR (0 если не важно)')

        match salary:
            case '0':
                salary = None
            case '8' | 'back':  # Возврат на предыдуший шаг
                self.__state = UIState.API_SEARCH0
                return False
            case '9' | 'exit':
                return True  # Завершение и выход
            case _:
                salary = int(salary) if salary.isnumeric() else None

        self.vacancies = []
        for api in self.apies:
            print(f'Начинаем парсинг {api} '
                  f'для вакансий по ключу "{keyword.upper()}"')
            vacancies = api.get_vacancy(keyword, salary)
            print(f'Найдено {len(vacancies)} с помощью {api}')
            self.vacancies.extend(vacancies)

        print(f'Используя {len(self.apies)} апи '
              f'получено {len(self.vacancies)} вакансий')
        self.__state = UIState.VACANCY
        return False  # Продолжаем работу в цикле

    def __working_with_vacancy(self) -> bool:

        print('(0) Установить кол-во вакансий в выдаче (деф. 10)'
              '\n(1) показать первые N вакансий'
              '\n(2) отсортировать по мин.з/п по уменьшению'
              '\n(3) отсортировать по мин.з/п по увеличению'
              '\n(4) отобрать вакансии по городу'
              '\n(5) отобрать вакансии по ключевому слову'
              '\n(6) отобрать вакансии по зарплате'
              '\n(x) сбросить текущие фильтры'
              '\n(s) сохранить текущую подборку в файл'
              '\n(a) сохранить все вакансии в файл'
              '\n(9, exit) выйти?')
        return True
