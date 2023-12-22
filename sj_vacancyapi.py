from datetime import datetime
from time import sleep

import httpx
from pydantic import BaseModel, Field
from rich import print

from currency_rate import CurrencyRate
from vacancy import Vacancy
from vacancyapi import VacancyApi


class SJVacancyAPI(VacancyApi):

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __str__(self) -> str:
        return 'SuperJob Api'

    def get_vacancy(self, keyword: str,
                    salary_from: int | None = None) -> list[Vacancy]:

        vacancy_list: list[Vacancy] = []
        return vacancy_list
