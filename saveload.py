from abc import ABC, abstractmethod
import json

from vacancy import Vacancy


class SaveLoadVacancies(ABC):

    @abstractmethod
    def loadfile(self, filename: str) -> list[Vacancy]:
        raise NotImplementedError

    @abstractmethod
    def savefile(self, vacancies: list[Vacancy], filename: str):
        raise NotImplementedError


class JSONSaveLoadVacancies(SaveLoadVacancies):

    def __init__(self) -> None:
        super().__init__()

    def loadfile(self, filename: str = 'vacancies.json') -> list[Vacancy]:

        vacancies: list[Vacancy] = []
        with open(filename) as jsonfile:
            data = json.load(jsonfile)
        for item in data:
            try:
                vacancy = Vacancy(**item)
                vacancies.append(vacancy)
            except Exception:
                print('При обработке файла возникла ошибка. Вероятно '
                      'файл поврежден. Возможно данные не полны.')
        return vacancies

    def savefile(self,
                 vacancies: list[Vacancy],
                 filename: str = 'vacancies.json'):

        vacancies_dict: list[dict] = []
        for vacancy in vacancies:
            vacancies_dict.append(vacancy.model_dump())

        with open(filename, 'w') as file:
            json.dump(vacancies_dict, file)
