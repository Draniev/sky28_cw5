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

    def add_one(self, model_data: dict):
        table_name = model_data.pop('table_name')

        # Creating a list of column names and values
        columns = ', '.join(model_data.keys())
        value_list = []
        for _, v in model_data.items():
            if isinstance(v, str):
                if "\'" in v:
                    v = v.replace("\'", "\'\'")
                value_list.append(f"'{v}'")
            elif v is None:
                value_list.append("null")
            else:
                value_list.append(str(v))
        values = ', '.join(value_list)

        # values = ', '.join(
        #     [f"'{v}'" if isinstance(v, str) else str(v)
        #         for _, v in model_data.items()])

        # Building the SQL query
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({
            values}) RETURNING *"

        # Executing the query and retrieving the result
        self.cursor.execute(query)
        new_obj = self.cursor.fetchone()

        # Committing the changes to the database
        self.conn.commit()
        return new_obj

    # def get_one_by_id(self, model_cls, obj_id: int):
    #     query = f"SELECT * FROM {model_cls.__name__} WHERE {
    #         model_cls.__name__.lower()}_id = %s"
    #     self.cursor.execute(query, (obj_id,))
    #     return self.cursor.fetchone()
    #
    # def get_one_by_name(self, model_cls, name: str):
    #     query = f"SELECT * FROM {model_cls.__name__} WHERE name = %s"
    #     self.cursor.execute(query, (name,))
    #     return self.cursor.fetchone()
    #
    # def get_all(self, model_cls) -> list[BaseModel]:
    #     query = f"SELECT * FROM {model_cls.__name__}"
    #     self.cursor.execute(query)
    #     return self.cursor.fetchall()
