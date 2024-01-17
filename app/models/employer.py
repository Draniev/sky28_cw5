from pydantic import BaseModel


class Employer(BaseModel, extra='ignore'):
    """
    МОДЕЛЬ из БД для объекта "Работодатель"
    """
    id: int
    # employer_hh_id: int
    name: str
    url: str | None
    description: str | None
    # open_vacancies: int

    def __repr__(self) -> str:
        """
        Возвращает ИМЯ ТАБЛИЦЫ в БД
        """
        return 'employers'
