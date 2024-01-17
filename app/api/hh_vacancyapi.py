from datetime import datetime
from time import sleep

import httpx
from pydantic import BaseModel, Field

from app.api.currency_rate import CurrencyRate
from app.api.vacancyapi import VacancyApi
from app.models.employer import Employer
from app.models.vacancy import Vacancy
from app.load_env import db


class HHEmployerShort(BaseModel):
    name: str
    id: int


class HHSalary(BaseModel):
    currency: str
    cur_from: int | None = Field(alias='from')
    cur_to: int | None = Field(alias='to')
    gross: bool


class HHVacancy(BaseModel, extra='ignore'):
    id: int
    name: str
    alternate_url: str
    area: dict
    created_at: datetime
    salary: HHSalary | None
    snippet: dict
    employer: HHEmployerShort


class HHResponse(BaseModel, extra='ignore'):
    found: int
    per_page: int
    pages: int
    page: int
    # items: list[HHVacancy]


class HHResponseVacancy(HHResponse):
    items: list[HHVacancy]


class HHResponseEmployers(HHResponse):
    items: list[HHEmployerShort]


class HHResponseEmployer(BaseModel, extra='ignore'):
    id: int
    name: str
    description: str | None
    open_vacancies: int
    site_url: str | None = Field(serialization_alias='url')
    trusted: bool


class HHVacancyAPI(VacancyApi):
    def __init__(self):
        self.base_url = 'https://api.hh.ru'
        self.rate = CurrencyRate()

    def __str__(self) -> str:
        return 'Head Hunter Api'

    def get_employers(self, keyword: str) -> list[Employer]:
        params = {
            'page': 0,
            'per_page': 100,
            'text': keyword
        }

        employers_list: list[Employer] = []
        hh_employers_list: list[HHEmployerShort] = []

        next_page = True
        while next_page:

            response = httpx.get(f'{self.base_url}/employers', params=params)

            try:
                hh_response = HHResponseEmployers(**response.json())
                hh_employers_list.extend(hh_response.items)
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

        employers_list = self.__convert_hh_employers(hh_employers_list)
        return employers_list

    def __convert_hh_employers(
            self,
            hh_employers: list[HHEmployerShort]) -> list[Employer]:
        employers: list[Employer] = []
        for hh_employer in hh_employers:
            print(f'Получаю полные данные по {hh_employer.name}')
            hh_full_employer = self.__get_full_employer(hh_employer.id)
            employer = Employer(**hh_full_employer.model_dump(by_alias=True))
            employers.append(employer)
            print(f'Данные по {hh_employer.name} получены')
            # employer_data = {
            #     "employer_id": hh_full_employer.id,
            #     "name": hh_full_employer.name,
            #     "url": hh_full_employer.site_url,
            #     "description": hh_full_employer.description,
            #     "table_name": "employers"
            # }
            # employer_obj = db.add_one(employer_data)
            # if employer_obj:
            #     employer = Employer(**employer_obj)
            #     employers.append(employer)
            #     print(f'В базу данных добавлен {hh_employer.name}'
            #           f'c ID {employer.employer_id}')
            # print(f'Всего добавлено {len(employers)} работодателей')
        return employers

    def __get_full_employer(self, employer_hh_id: int) -> HHResponseEmployer:
        response = httpx.get(f'{self.base_url}/employers/{employer_hh_id}')
        hh_employer = HHResponseEmployer(**response.json())
        return hh_employer

    def get_vacancy(self, keyword: str | None = None,
                    salary_from: int | None = None,
                    employer_id: int | None = None) -> list[Vacancy]:

        params = {
            'page': 0,
            'per_page': 100,
        }
        if keyword:
            params['text'] = keyword
        if salary_from:
            params['salary'] = salary_from
            params['only_with_salary'] = True
        if employer_id:
            params['employer_id'] = employer_id

        vacancies_list: list[Vacancy] = []
        hh_vacancies_list: list[HHVacancy] = []

        next_page = True
        while next_page:

            response = httpx.get(f'{self.base_url}/vacancies', params=params)

            try:
                hh_response = HHResponseVacancy(**response.json())
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
            description = hh_vac.snippet['responsibility']
            area_name = hh_vac.area.get('name')
            if hh_vac.salary:
                salary_from, salary_to = self.__get_salary_in_rur(
                    hh_vac.salary)
            else:
                salary_from = None
                salary_to = None

            vacancy_data = {
                'id': hh_vac.id,
                'name': name,
                'url': url,
                'description': description,
                'salary_from': salary_from,
                'salary_to': salary_to,
                'area_name': area_name,
                'employer_id': hh_vac.employer.id,
            }
            vacancy = Vacancy(**vacancy_data)
            vacancies.append(vacancy)

            # vacancy_obj = db.add_one(vacancy_data)
            # if vacancy_obj:
            #     vacancy = Vacancy(**vacancy_obj)
            #     vacancies.append(vacancy)

        return vacancies

    def __get_salary_in_rur(self,
                            salary: HHSalary) -> tuple[int | None, int | None]:

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
