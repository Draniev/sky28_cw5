import psycopg2

from app.load_env import db_params


def main():
    conn = None

    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute('DROP TABLE vacancies;')
                cur.execute('DROP TABLE employees;')
                print("Таблицы успешно удалены")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
