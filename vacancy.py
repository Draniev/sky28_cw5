from pydantic import BaseModel


class Vacancy(BaseModel, extra='ignore'):
    name: str
    url: str
    description: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    # currency: str | None = None
    area_name: str | None = None  # Moсква

    def __eq__(self, __value: object) -> bool:
        pass

    def __lt__(self, __value: object) -> bool:
        pass

    def __le__(self, __value: object) -> bool:
        pass

    def __str__(self) -> str:
        pass
