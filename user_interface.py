from enum import Enum

from rich import print
from saveload import JSONSaveLoadVacancies

from hh_vacancyapi import HHVacancyAPI
from load_env import SJ_API_KEY
from sj_vacancyapi import SJVacancyAPI
from vacancy import Vacancy
from vacancyapi import VacancyApi


class UIState(Enum):
    IDLE = 'Ожидаем начала работы'
    LOAD = 'Работа с БД'
    API_SEARCH0 = 'Добавить работодателя в БД'
    API_SEARCH1 = 'Загружаем критерии поиска вакансий'
    # VACANCY = 'Режим работы с загруженными вакансиями'
    EXIT = 'Выключаемся'


class UserInterface:

    def __init__(self):
        self.__state = UIState.IDLE
        self.hh_api = HHVacancyAPI()
        # self.sj_api = SJVacancyAPI(SJ_API_KEY)
        self.apies: list[VacancyApi] = []
        self.vacancies: list[Vacancy] = []  # Локальная выборка для работы
        self.print_qty: int = 10  # количество объектов на печать

        self.apies.append(self.hh_api)

    def start(self):
        is_exit = False

        while not is_exit:
            is_exit = self.__hello_ui()

        print('Досвидули, я закрываюсь')

    def __hello_ui(self) -> bool:

        match self.__state:
            case UIState.IDLE:
                is_exit = self.__idle_input()
            case UIState.LOAD:
                is_exit = self.__working_with_vacancy()
            case UIState.API_SEARCH0:
                is_exit = self.__search0_input()
            case UIState.API_SEARCH1:
                is_exit = self.__add_employee_do_db()
            # case UIState.VACANCY:
            #     is_exit = self.__working_with_vacancy()
            case _:
                is_exit = True  # В любой не понятной ситуации - досвидули!

        # print(self.__state)
        # print(f'is_exit: {is_exit}')
        return is_exit

    def __idle_input(self) -> bool:

        print('(1) Поработать с БАЗОЙ или '
              '\n(2) добавить новые компании, '
              '\n(9, exit) выйти?')

        user_input = input('Выберите действие: 1, 2 или 9 >> ')

        match user_input:
            case '1':
                self.__state = UIState.LOAD
            case '2':
                self.__state = UIState.API_SEARCH0
            case '9' | 'exit':
                return True  # Завершение и выход

        return False

    def __add_employee_do_db(self) -> bool:

        keyword = input('(8, back) назад или выйти (9, exit)\n'
                        'Название работодателя для парсинга')

        match keyword:
            case '8' | 'back':  # Возврат на предыдуший шаг
                self.__state = UIState.IDLE
                return False
            case '9' | 'exit':
                return True  # Завершение и выход

        self.vacancies = []
        for api in self.apies:
            print(f'Начинаем парсинг {api} '
                  f'для вакансий по ключу "{keyword.upper()}"')
            # vacancies = api.get_vacancy(keyword, salary)
            print(f'Найдено {len(vacancies)} с помощью {api}')
            self.vacancies.extend(vacancies)

        print(f'Используя {len(self.apies)} апи '
              f'получено {len(self.vacancies)} вакансий')
        self.__state = UIState.IDLE
        return False  # Продолжаем работу в цикле

    def __working_with_vacancy(self) -> bool:
        """
        Пользовательский интерфейс для работы с сохранённым (загруженным)
        в памятя списком вакансий. Доступна фильтрация, всякий вывод и пр.
        При желании тут можно было бы много всего придумать...
        """

        print('(0) Установить кол-во вакансий в выдаче (деф. 10)'
              '\n(1) показать первые N вакансий'
              '\n(2) отсортировать по з/п по уменьшению'
              '\n(3) отсортировать по з/п по увеличению'
              '\n(4) отобрать вакансии по городу'
              '\n(5) отобрать вакансии по ключевому слову'
              '\n(s) сохранить вакансии в файл'
              '\n(9, exit) выйти?')
        action = input('Выберите действие: 0-6, x, s, a, 9 >> ')

        match action:
            case '0':  # Установить отображение N на страницу
                self.__set_print_qty()
            case '1':  # Напечатать первый N вакансий
                self.__print_per_page()
            case '2':  # Отсортировать по уменьшинию
                self.__sort_by_salary(True)
            case '3':  # Отсортировать по увеличению
                self.__sort_by_salary()
            case '4':
                self.__filter_city()
            case '5':
                self.__filter_word()
            case '9' | 'exit':
                return True  # Завершение и выход

        return False

    def __set_print_qty(self) -> None:
        qty = input('Укажите кол-во объектов для вывода на печать: ')
        try:
            qty = int(qty)
            self.print_qty = qty
        except Exception:
            print(f'Что-то пошло не так, предыдущее значение '
                  f'({self.print_qty}) не изменилось')

    def __print_vacancies_page(self, page: int = 0) -> None:
        print(f'Объекты вакансий с {page * self.print_qty + 1} по '
              f'{page * self.print_qty + self.print_qty}')
        for i in range(self.print_qty):
            print(self.vacancies[page * self.print_qty + i].__str__())
        print('\n[bold]#################[/bold]')

    def __print_per_page(self) -> None:
        # Тут мне очень лень возиться с возможной "последней"
        # страницей, которая может оказаться не полной, так
        # что позволю себе от неё избавиться. Тем более в задаче
        # подобного вообще не было.
        pages = len(self.vacancies) // self.print_qty
        for i in range(pages):
            self.__print_vacancies_page(i)
            is_next = input('Enter -> дальше, Any simbol -> стоп >> ')
            if len(is_next) != 0:
                break

    def __sort_by_salary(self, reverse=False) -> None:
        self.vacancies.sort(reverse=reverse)

    def __filter_city(self) -> bool:

        city = input('(8, back) назад\n'
                     'Введите город для выбоорки >> ')

        match city:
            case '8' | 'back':  # Возврат на предыдуший шаг
                return False
            case _:
                pass

        filtered = filter(lambda x: x.area_name == city, self.vacancies)
        self.vacancies = list(filtered)

        return True  # Продолжаем работу в цикле

    def __filter_word(self) -> bool:

        key = input('(8, back) назад\n'
                    'Введите ключ для фильтрации выборки >> ')

        match key:
            case '8' | 'back':  # Возврат на предыдуший шаг
                return False
            case _:
                pass

        filtered = filter(lambda x: key in (x.name,
                                            x.description,
                                            x.area_name,
                                            ),
                          self.vacancies)
        self.vacancies = list(filtered)

        return True  # Продолжаем работу в цикле
