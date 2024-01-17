from types import new_class
# from app.service.db_manager import DBManager
from app.load_env import db_params, db
from app.models.employer import Employer
from app.models.vacancy import Vacancy

# db = DBManager(**db_params)


# Example 1: Adding an Employer
employer_data = {
    "employer_id": 1,
    # "employer_hh_id": 23450,
    "name": "ABC Corp",
    "url": "https://www.abccorp.com",
    "description": "A sample employer",
    "table_name": "employers"
}

# employer = Employer(**employer_data)
new_obj = db.add_one(employer_data)
print(new_obj)
if new_obj:
    employer = Employer(**new_obj)
    print(employer)

# if new_obj:
#     employer = Employer(
#         employer_id=new_obj[0],
#         employer_hh_id=new_obj[1],
#         name=new_obj[2],
#         url=new_obj[3],
#         description=new_obj[4])
#     print(employer)
