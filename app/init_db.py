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


def create_tables(cur) -> None:
    cur.execute('CREATE TABLE employers('
                # 'employer_id SERIAL PRIMARY KEY, '
                'employer_id INT PRIMARY KEY, '
                'name VARCHAR(255) NOT NULL, '
                'url VARCHAR(255) NOT NULL, '
                'description TEXT'
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
                'employer_id INT REFERENCES employers(employer_id) '
                ');')


if __name__ == "__main__":
    main()
