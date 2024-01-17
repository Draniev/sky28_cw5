from enum import Enum
from typing import Any

from rich import print

from app.api.hh_vacancyapi import HHVacancyAPI
from app.models.vacancy import Vacancy
from app.models.employer import Employer

from app.load_env import db


class UIState(Enum):
    IDLE = 'Ожидаем начала работы'
    BD_LOAD = 'Работа с БД'
    API_SEARCH0 = 'Добавить работодателя в БД'
    EXIT = 'Выключаемся'


class UserInterface:

    def __init__(self):
        self.__state = UIState.IDLE
        self.vacancies: list[Vacancy] = []  # Локальная выборка для работы
        self.print_qty: int = 10  # количество объектов на печать

        self.hh_api = HHVacancyAPI()

    def start(self):
        is_exit = False

        while not is_exit:
            is_exit = self.__hello_ui()

        print('Досвидули, я закрываюсь')

    def __hello_ui(self) -> bool:

        match self.__state:
            case UIState.IDLE:
                is_exit = self.__idle_input()
            case UIState.BD_LOAD:
                is_exit = self.__working_with_vacancy()
            case UIState.API_SEARCH0:
                is_exit = self.__add_employee_do_db()
            case _:
                is_exit = True  # В любой не понятной ситуации - досвидули!

        return is_exit

    def __idle_input(self) -> bool:

        print('(1) Поработать с БАЗОЙ или '
              '\n(2) добавить новые компании '
              '\n(9, exit) выйти?')

        user_input = input('Выберите действие: 1, 2 или 9 >> ')

        match user_input:
            case '1':
                self.__state = UIState.BD_LOAD
            case '2':
                self.__state = UIState.API_SEARCH0
            case '9' | 'exit':
                return True  # Завершение и выход

        return False

    def __add_employee_do_db(self) -> bool:
        """
        Ищет работодателей по ключевому слову и добавляет их в базу данных!
        """

        keyword = input('(8, back) назад или выйти (9, exit)\n'
                        'Название работодателя для парсинга >>  ')

        match keyword:
            case '8' | 'back':  # Возврат на предыдуший шаг
                self.__state = UIState.IDLE
                return False
            case '9' | 'exit':
                return True  # Завершение и выход

        # Парсим все КОМПАНИИ
        print(f'Начинаем парсинг {self.hh_api} '
              f'для поискa "{keyword.upper()}"')
        employers = self.hh_api.get_employers(keyword)
        print(f'Найдено {len(employers)} с помощью {self.hh_api}')

        # Добавляем КОМПАНИИ в БД
        employers_to_db = []
        for employer in employers:
            is_add = input(f'{employer.name.upper()} '
                           'добавляем? (n-нeт, y-да) >> ')
            match is_add:
                case 'n' | 'n' | 'нет':
                    print('ок, пропустили, удалили, забыли')
                case 'y' | 'Y' | 'да':
                    employers_to_db.append(employer)
                    is_added = db.add_one_new(employer)
                    if is_added:
                        print(f'Успешно добавлен в БД: {employer.name}')
                    else:
                        print(f'Не получилось добавить {employer.name}, ай ай')

        # Парсим вакансии работодателей
        print('Начинаем парсинг вакансий для найденых работодателей')
        for employer in employers_to_db:
            v_list = self.hh_api.get_vacancy(employer_id=employer.id)
            for vac in v_list:
                db.add_one_new(vac)
            print(f'Добавлено {len(v_list)}, вакансий для {employer.name}')

        self.__state = UIState.IDLE
        return False  # Продолжаем работу в цикле

    def __working_with_vacancy(self) -> bool:
        """
        Пользовательский интерфейс для работы с сохранённым (загруженным)
        в памятя списком вакансий. Доступна фильтрация, всякий вывод и пр.
        При желании тут можно было бы много всего придумать...
        """

        print('\n(0) Установить кол-во вакансий в выдаче (деф. 10)'
              '\n(1) список всех компаний и кол-во вакансий по ним'
              '\n(2) список всех вакансий включая назв. компании, ссылку, з/п'
              '\n(3) средняя зарплата по загруженным вакансиям'
              '\n(4) все вакансии с з/п выше средней'
              '\n(5) поиск в названии вакансии по слову'
              '\n(8, back) назад'
              '\n(9, exit) выйти?')
        action = input('Выберите действие: 0-6, 8, 9 >> ')

        match action:
            case '0':  # Установить отображение N на страницу
                self.__set_print_qty()
            case '1':  # Напечатать первый N вакансий
                self.__print_all_companies()
            case '2':  # Отсортировать по уменьшинию
                self.__print_all_vacancies()
            case '3':  # Отсортировать по увеличению
                self.__print_avg_salary()
            case '4':
                self.__print_vac_w_salary_qt_avg()
            case '5':
                self.__find_vacancy_by_word()
            case '8' | 'back':  # Возврат на предыдуший шаг
                self.__state = UIState.IDLE
                return False
            case '9' | 'exit':
                return True  # Завершение и выход

        return False

    def __print_all_companies(self):
        print('\nВот список всех компаний и кол-ва вакансий по ним:')
        companies = db.get_companies_and_vacancies_count()
        print(companies)

    def __print_all_vacancies(self):
        print('\n[bold]Вот постраничный список всех вакансий:[/bold] ')
        vacancy_dict = db.get_all_vacancies()
        self.__print_per_page(vacancy_dict)

    def __print_avg_salary(self):
        average = db.get_avg_salary()
        print(f'\n[bold]Средняя зарплата по загруженным вакансиям:[/bold] {average}')

    def __print_vac_w_salary_qt_avg(self):
        print('\n[bold]Постраничный спосок вакансий с з/п выше средней[/bold]')
        vacancies = db.get_vacancies_with_higher_salary()
        self.__print_per_page(vacancies)

    def __find_vacancy_by_word(self) -> bool:

        key = input('(8, back) назад\n'
                    'Введите ключ для поиска вакансии >> ')

        match key:
            case '8' | 'back':  # Возврат на предыдуший шаг
                return False
            case _:
                pass

        vacancies = db.get_vacancies_with_keyword(key)
        print('[bold]Вот постраничный список запрошенных вакансий:[/bold] ')
        self.__print_per_page(vacancies)

        return True  # Продолжаем работу в цикле

    def __set_print_qty(self) -> None:
        qty = input('Укажите кол-во объектов для вывода на печать: ')
        try:
            qty = int(qty)
            self.print_qty = qty
        except Exception:
            print(f'Что-то пошло не так, предыдущее значение '
                  f'({self.print_qty}) не изменилось')

    def __print_page_num_i(self, data: list[Any], page: int = 0) -> None:
        print(f'Объекты вакансий с {page * self.print_qty + 1} по '
              f'{page * self.print_qty + self.print_qty}')
        for i in range(self.print_qty):
            print(data[page * self.print_qty + i].__str__())
        print('\n')

    def __print_per_page(self, data: list[Any]) -> None:
        # Тут мне очень лень возиться с возможной "последней"
        # страницей, которая может оказаться не полной, так
        # что позволю себе от неё избавиться. Тем более в задаче
        # подобного вообще не было.
        pages = len(data) // self.print_qty
        for i in range(pages):
            self.__print_page_num_i(data=data, page=i)
            is_next = input('Enter -> дальше, Any simbol -> стоп >> ')
            if len(is_next) != 0:
                break
