from pydantic import BaseModel


class Vacancy(BaseModel, extra='ignore'):
    id: int
    # vacancy_hh_id: int
    name: str
    url: str
    employer_id: int
    description: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    area_name: str | None = None  # Moсква

    def __repr__(self) -> str:
        """
        Возвращает ИМЯ ТАБЛИЦЫ в БД
        """
        return 'vacancies'

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Vacancy):
            if self.salary_to:
                if __value.salary_to and __value.salary_from:
                    return self.salary_to == __value.salary_to
                elif __value.salary_to:
                    return self.salary_to == __value.salary_to
                elif __value.salary_from:
                    return False
                else:
                    return True
            elif self.salary_from:
                if __value.salary_to and __value.salary_from:
                    return self.salary_from == __value.salary_from
                elif __value.salary_to:
                    return False
                elif __value.salary_from:
                    return self.salary_from == __value.salary_from
                else:
                    return False
            else:
                if __value.salary_to or __value.salary_from:
                    return False
                else:
                    return True
        else:
            raise ValueError

    def __lt__(self, __value: object) -> bool:
        if isinstance(__value, Vacancy):
            if self.salary_to:
                if __value.salary_to and __value.salary_from:
                    return self.salary_to < __value.salary_to
                elif __value.salary_to:
                    return self.salary_to < __value.salary_to
                elif __value.salary_from:
                    return self.salary_to < __value.salary_from
                else:
                    return False
            elif self.salary_from:
                if __value.salary_to and __value.salary_from:
                    return self.salary_from < __value.salary_from
                elif __value.salary_to:
                    return self.salary_from < __value.salary_to
                elif __value.salary_from:
                    return self.salary_from < __value.salary_from
                else:
                    return False
            else:
                if __value.salary_to or __value.salary_from:
                    return True
                else:
                    return False
        else:
            raise ValueError

    def __le__(self, __value: object) -> bool:
        if isinstance(__value, Vacancy):
            if self.salary_to:
                if __value.salary_to and __value.salary_from:
                    return self.salary_to <= __value.salary_to
                elif __value.salary_to:
                    return self.salary_to <= __value.salary_to
                elif __value.salary_from:
                    return self.salary_to < __value.salary_from
                else:
                    return False
            elif self.salary_from:
                if __value.salary_to and __value.salary_from:
                    return self.salary_from <= __value.salary_from
                elif __value.salary_to:
                    return self.salary_from < __value.salary_to
                elif __value.salary_from:
                    return self.salary_from <= __value.salary_from
                else:
                    return False
            else:
                return True
        else:
            raise ValueError

    def __str__(self) -> str:
        if self.salary_to and self.salary_from:
            str = (f'\n[bold]{self.name}[/bold]: {self.url}'
                   f'\nв городe {self.area_name}.'
                   f'\n{self.description}'
                   f'\nЗарплата [bold]от {self.salary_from} до {self.salary_to}[/bold] руб.')
        elif self.salary_to:
            str = (f'\n[bold]{self.name}[/bold]: {self.url}'
                   f'\nв городe {self.area_name}.'
                   f'\n{self.description}'
                   f'\nЗарплата [bold]до {self.salary_to}[/bold] руб.')
        elif self.salary_from:
            str = (f'\n[bold]{self.name}[/bold]: {self.url}'
                   f'\nв городe {self.area_name}.'
                   f'\n{self.description}'
                   f'\nЗарплата [bold]от {self.salary_from}[/bold] руб.')
        else:
            str = (f'\n[bold]{self.name}[/bold]: {self.url}'
                   f'\nв городe {self.area_name}.'
                   f'\n{self.description}'
                   f'\nЗарплата не указана!')

        return str
