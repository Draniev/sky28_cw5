from abc import ABC, abstractmethod

from vacancy import Vacancy


class VacancyApi(ABC):

    @abstractmethod
    def get_vacancy(self, keyword: str,
                    salary_from: int | None = None) -> list[Vacancy]:
        raise NotImplementedError
