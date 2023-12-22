from datetime import datetime
from time import sleep

import httpx
from pydantic import BaseModel, Field

from currency_rate import CurrencyRate
from vacancy import Vacancy
from vacancyapi import VacancyApi


class HHSalary(BaseModel):
    currency: str
    cur_from: int | None = Field(alias='from')
    cur_to: int | None = Field(alias='to')
    gross: bool


class HHVacancy(BaseModel, extra='ignore'):
    name: str
    alternate_url: str
    area: dict
    created_at: datetime
    salary: HHSalary | None
    description: str | None = None


class HHResponse(BaseModel, extra='ignore'):
    found: int
    per_page: int
    pages: int
    page: int
    items: list[HHVacancy]


class HHVacancyAPI(VacancyApi):

    def __init__(self):
        self.base_url = 'https://api.hh.ru'
        self.rate = CurrencyRate()

    def __str__(self) -> str:
        return 'Head Hunter Api'

    def get_vacancy(self, keyword: str,
                    salary_from: int | None = None) -> list[Vacancy]:

        params = {
            'page': 0,
            'per_page': 100,
            'text': keyword,
        }
        if salary_from:
            params['salary'] = salary_from
            params['only_with_salary'] = True

        vacancies_list: list[Vacancy] = []
        hh_vacancies_list: list[HHVacancy] = []

        response = httpx.get(f'{self.base_url}/vacancies', params=params)

        next_page = True
        while next_page:

            response = httpx.get(f'{self.base_url}/vacancies', params=params)

            try:
                hh_response = HHResponse(**response.json())
                hh_vacancies_list.extend(hh_response.items)
                params['page'] = hh_response.page + 1

                if params['page'] == hh_response.pages:
                    next_page = False
                else:
                    #  Задержка чтобы ХХ не слишком волновался
                    sleep(0.5)

            except Exception:
                pass
                # Если переборщить с кол-м запромов то может начать
                # сыпать ошибки... пропустим их

        vacancies_list = self.__convert_hh_vacancies(hh_vacancies_list)

        return vacancies_list

    def __convert_hh_vacancies(self,
                               hh_vacancies: list[HHVacancy]) -> list[Vacancy]:
        vacancies: list[Vacancy] = []

        for hh_vac in hh_vacancies:
            name = hh_vac.name
            url = hh_vac.alternate_url
            description = hh_vac.description
            area_name = hh_vac.area.get('name')
            if hh_vac.salary:
                salary_from, salary_to = self.__get_salary_in_rur(
                    hh_vac.salary)
            else:
                salary_from = None
                salary_to = None

            vacancy = Vacancy(name=name, url=url, description=description,
                              area_name=area_name, salary_from=salary_from,
                              salary_to=salary_to)
            vacancies.append(vacancy)

        return vacancies

    def __get_salary_in_rur(self, salary: HHSalary) -> tuple[int | None, int | None]:

        if salary.currency == 'RUR':
            salary_from = salary.cur_from
            salary_to = salary.cur_to
        else:
            if salary.cur_from:
                try:
                    salary_from = int(self.rate.conv_to_rur(salary.cur_from,
                                                            salary.currency))
                except KeyError:
                    # Ну какого черта у ЦБРФ и ХХ разные коды для БелРуб?
                    salary_from = None
            else:
                salary_from = None
            if salary.cur_to:
                try:
                    salary_to = int(self.rate.conv_to_rur(salary.cur_to,
                                                          salary.currency))
                except KeyError:
                    salary_to = None
            else:
                salary_to = None

        return salary_from, salary_to
