from enum import Enum


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

    def start(self):
        is_exit = False

        while not is_exit:
            is_exit = self.__hello_ui()

        print('Досвидули, я закрываюсь')

    def __hello_ui(self) -> bool:

        match self.__state:

            case UIState.IDLE:
                print('Хотите поработать с локальными файлами (1) '
                      'или загрузить новые вакансии (2), '
                      'или выйти (exit, 3)?')
                user_input = input('Выберите действие: 1, 2 или 3 >> ')
                is_exit = self.__parse_idle_input(user_input)

            case UIState.LOAD_FILE:
                is_exit = True

            case UIState.API_SEARCH0:
                print('Хотите поискать на всех доступных платформах (0), '
                      ' или на ХХ (1) '
                      'или на SuperJob (2), '
                      'или выйти (exit, 3)?')
                user_input = input('Выберите действие: 0, 1, 2 или 3 >> ')
                is_exit = self.__parse_search0_input(user_input)
                is_exit = True

            case UIState.API_SEARCH1:
                is_exit = True

            case UIState.VACANCY:
                is_exit = True

            case _:
                is_exit = True  # Выход если что-то не внятное

        print(f'is_exit: {is_exit}')
        return is_exit

    def __parse_idle_input(self, input: str) -> bool:

        match input:
            case '1':
                self.__state = UIState.LOAD_FILE
            case '2':
                self.__state = UIState.API_SEARCH0
            case '3' | 'exit':
                return True  # Завершение и выход

        return False

    def __parse_search0_input(self, input: str) -> bool:

        match input:
            case '0':
                pass
            case '1':
                pass
            case '2':
                pass
            case '3' | 'exit':
                return True  # Завершение и выход

        self.__state = UIState.API_SEARCH1
        return False
