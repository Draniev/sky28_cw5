import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from app.models.employer import Employer
from app.models.vacancy import Vacancy


class DBManager:
    def __init__(self, user, password, dbname, host, port):
        self.conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            dbname=dbname,
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def add_one_new(self, model: BaseModel) -> bool:
        table_name = model.__repr__()
        model_dict = model.model_dump()

        # Creating a list of column names and values
        columns = ', '.join(model_dict.keys())
        value_list = []
        for _, v in model_dict.items():
            if isinstance(v, str):
                if "\'" in v:
                    v = v.replace("\'", "\'\'")
                value_list.append(f"'{v}'")
            elif v is None:
                value_list.append("null")
            else:
                value_list.append(str(v))
        values = ', '.join(value_list)

        # Building the SQL query
        query = (f"INSERT INTO {table_name} ({columns}) "
                 f"VALUES ({values})")

        try:
            # Executing the query
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Добавить в БД {model.name} не вышло!')
            print(e)
            return False

    def get_companies_and_vacancies_count(self):
        """
        получает список всех компаний
        и количество вакансий у каждой компании
        """
        query = (
            "SELECT employers.name, COUNT(*) FROM vacancies "
            "LEFT JOIN employers ON vacancies.employer_id = employers.id "
            "GROUP BY employers.name; "
        )
        self.cursor.execute(query)
        request = self.cursor.fetchall()
        return [dict(item) for item in request]

    def get_all_vacancies(self):
        """
        получает список всех вакансий
        с указанием названия компании, названия вакансии и зарплаты
        и ссылки на вакансию
        """
        query = (
            "SELECT employers.name, vacancies.name, salary_from, salary_to, "
            "vacancies.url FROM vacancies "
            "LEFT JOIN employers ON vacancies.employer_id = employers.id;"
        )
        self.cursor.execute(query)
        request = self.cursor.fetchall()
        return [dict(item) for item in request]

    def get_avg_salary(self) -> int:
        """
        получает среднюю зарплату по вакансиям
        """
        query = (
            "SELECT AVG(salary_from) as salary_from, "
            "AVG(salary_to) as salary_to FROM vacancies;"
        )
        self.cursor.execute(query)
        request = self.cursor.fetchone()
        avg = (request['salary_from'] + request['salary_to']) / 2
        return int(avg)

    def get_vacancies_with_higher_salary(self) -> list[Vacancy]:
        """
        получает список всех вакансий, у которых
        зарплата выше средней по всем вакансиям
        """
        avg = self.get_avg_salary()
        query = (
            "SELECT * FROM vacancies "
            f"WHERE salary_from > {avg}"
        )
        self.cursor.execute(query)
        request = self.cursor.fetchall()
        return [Vacancy(**item) for item in request]

    def get_vacancies_with_keyword(self, keyword: str) -> list[Vacancy]:
        """
        получает список всех вакансий, в названии которых
        содержатся переданные в метод слова
        """
        query = (
            "SELECT * FROM vacancies "
            f"WHERE name LIKE '%{keyword}%'"
        )
        self.cursor.execute(query)
        request = self.cursor.fetchall()
        return [Vacancy(**item) for item in request]
