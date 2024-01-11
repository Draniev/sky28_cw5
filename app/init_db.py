import psycopg2

from app.load_env import db_params


def main():
    conn = None

    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                create_tables(cur)
                print("Таблицы успешно созданы")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# def create_database(params, db_name) -> None:
#     """Создает новую базу данных."""
#     conn = psycopg2.connect(**params)
#     conn.autocommit = True
#     cur = conn.cursor()
#     cur.execute(f'CREATE DATABASE {db_name};')
#     conn.close()


def create_tables(cur) -> None:
    cur.execute('CREATE TABLE employees('
                'employer_id SERIAL PRIMARY KEY, '
                'employer_hh_id INT NOT NULL, '
                'name VARCHAR(255) NOT NULL, '
                'url VARCHAR(255) NOT NULL, '
                'description VARCHAR(255) '
                ');')

    cur.execute('CREATE TABLE vacancies('
                'vacancy_id SERIAL PRIMARY KEY, '
                'vacancy_hh_id INT NOT NULL, '
                'name VARCHAR(255) NOT NULL, '
                'url VARCHAR(255) NOT NULL, '
                'description VARCHAR(255), '
                'salary_from INT, '
                'salary_to INT, '
                'area_name VARCHAR(255), '
                'employer_id INT REFERENCES employees(employer_id) '
                ');')


if __name__ == "__main__":
    main()
