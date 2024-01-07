from pydantic import BaseModel


class Employer(BaseModel, extra='ignore'):
    employer_id: int
    employer_hh_id: int
    name: str
    url: str
    description: str
