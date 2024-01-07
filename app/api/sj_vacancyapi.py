from datetime import datetime
from time import sleep

import httpx
from pydantic import BaseModel
from rich import print

from currency_rate import CurrencyRate
from vacancy import Vacancy
from vacancyapi import VacancyApi


class SJErrorCode(BaseModel):
    """
    Код	Описание
    400	Неверно переданы параметры. В описании ошибки, как правило,
        указываются все необходимые параметры.
    401	Требуется авторизация
    403	Доступ запрещён. Ошибки доступа.
    404	Сущность не найдена. Например, при отправке несуществующего
        email с запросом на восстановление пароля.
    410	Срок актуальности сущности истёк. (Expired)
    422	Ошибки валидации при вставке или апдейте сущностей
    429	Превышено ограничение по частоте запросов или по общему их количеству
    504	Системная ошибка API.
    """
    code: int
    message: str


class SJAPIError(BaseModel):
    error: SJErrorCode


class SJVacancy(BaseModel, extra='ignore'):
    profession: str
    work: str | None  # Описание вакансии
    candidat: str | None
    payment_from: int
    payment_to: int
    currency: str
    date_published: datetime
    town: dict
    firm_name: str
    link: str


class SJResponse(BaseModel, extra='ignore'):
    total: int  # Общее кол-во результатов
    more: bool  # Есть ли еще результаты
    objects: list[SJVacancy]


class SJVacancyAPI(VacancyApi):

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = 'https://api.superjob.ru/2.0'
        self.rate = CurrencyRate()

    def __str__(self) -> str:
        return 'SuperJob Api'

    def get_vacancy(self, keyword: str,
                    salary_from: int | None = None) -> list[Vacancy]:

        headers = {
            'X-Api-App-Id': self.api_key
        }

        curr_page = 0
        params = {
            'page': curr_page,
            'count': 100,  # Кол-во результатов на страницу поиска
            'keyword': keyword,
        }

        if salary_from:
            params['payment_from'] = salary_from
            params['no_agreenent'] = 1  # Не показывать вакансии без з/п

        vacancies: list[Vacancy] = []
        sj_vacancies: list[SJVacancy] = []

        next_page = True
        while next_page:

            response = httpx.get(f'{self.base_url}/vacancies/',
                                 params=params, headers=headers)

            try:
                sj_response = SJResponse(**response.json())
                sj_vacancies.extend(sj_response.objects)

                if sj_response.more is True:
                    curr_page += 1
                    params['page'] = curr_page
                    next_page = True
                    sleep(0.1)  # Задержка чтобы SJ не слишком волновался
                else:
                    next_page = False

            except Exception as e:
                print('Какая то фигня в цикле десереализации')
                print(e)
                next_page = False
                # Если переборщить с кол-м запромов то может начать
                # сыпать ошибки... пропустим их

        vacancies = self.__convert_sj_vacancies(sj_vacancies)

        return vacancies

    def __convert_sj_vacancies(self,
                               sj_vacancies: list[SJVacancy]) -> list[Vacancy]:
        vacancies: list[Vacancy] = []

        for sj_vac in sj_vacancies:
            name = sj_vac.profession
            url = sj_vac.link
            description = sj_vac.candidat
            area_name = sj_vac.town.get('title')

            if sj_vac.payment_from:
                if sj_vac.currency == 'rub':
                    salary_from = sj_vac.payment_from
                else:
                    salary_from = int(
                        self.rate.conv_to_rur(sj_vac.payment_from,
                                              sj_vac.currency))
            else:
                salary_from = None

            if sj_vac.payment_to:
                if sj_vac.currency == 'rub':
                    salary_to = sj_vac.payment_to
                else:
                    salary_to = int(
                        self.rate.conv_to_rur(sj_vac.payment_to,
                                              sj_vac.currency))
            else:
                salary_to = None

            vacancy = Vacancy(name=name, url=url, description=description,
                              area_name=area_name, salary_from=salary_from,
                              salary_to=salary_to)
            vacancies.append(vacancy)

        return vacancies
