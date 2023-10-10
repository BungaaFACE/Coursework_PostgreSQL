import psycopg2
from vacancy import Vacancy
from os import getenv
from tabulate import tabulate


class PostgresAPI:
    def __enter__(self):
        try:
            self.conn = self.get_connect(db_name='hh_parser')

        except psycopg2.OperationalError:
            # Create DB
            with self.get_connect() as postgres_conn:
                with postgres_conn.cursor() as cursor:
                    cursor.execute("CREATE DATABASE hh_parser;")
                postgres_conn.commit()
            # Connect to new DB
            self.conn = self.get_connect(db_name='hh_parser')
            # Create new tables
            with open('create_tables.sql', encoding='utf-8') as file:
                sql_exec = file.read()
            self.custom_request(sql_exec)
            self.conn.commit()

        finally:
            return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    def get_connect(self, db_name='postgres'):
        conn = psycopg2.connect(
            host='localhost',
            database=db_name,
            user='postgres',
            password=getenv('POSTGRES_PASSWORD')
        )
        return conn

    def insert_company(self, company):
        """
            company_id INTEGER PRIMARY KEY NOT NULL,
            company_name VARCHAR(50),
            company_url VARCHAR(100)
        """
        company_id = company['id']
        company_name = company['name']
        company_url = company['url']

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                f"INSERT INTO companies(company_id, company_name, company_url) VALUES ({company_id}, '{company_name}', '{company_url}')")
        except psycopg2.errors.UniqueViolation:
            print('Компания и ее вакансии уже сохранены. Если вы хотите обновить список вакансий, то прежде выберите пункт меню 7 (удаление записей).')
            return False
        cursor.close()
        return True

    def insert_list_of_vacancies(self):
        """
            vacancy_id SERIAL PRIMARY KEY NOT NULL,
            vacancy_name VARCHAR(50) NOT NULL,
            avg_salary INTEGER,
            vacancy_address VARCHAR(100),
            vacancy_url VARCHAR(100),
            company_id INTEGER REFERENCES companies(company_id)
        """
        cursor = self.conn.cursor()
        cursor.executemany(
            f"INSERT INTO vacancies(vacancy_name, avg_salary, vacancy_address, vacancy_url, company_id) VALUES (%s, %s, %s, %s, %s)",
            [(vacancy.vacancy_name, vacancy.avg_salary, vacancy.vacancy_address, vacancy.vacancy_url, vacancy.company_id) for vacancy in Vacancy.all_vacancies])
        Vacancy.clear_vacancies()
        cursor.close()

    def custom_request(self, sql_exec, return_data=False):
        cur = self.conn.cursor()
        cur.execute(sql_exec)
        if return_data:
            colnames = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            cur.close()
            return colnames, data
        cur.close()

    def get_companies_and_vacancies_count(self, print_result=True):
        sql_exec = "SELECT company_name, COUNT(vacancies.vacancy_id) AS number_of_vacancies FROM companies "\
            'JOIN vacancies USING(company_id) '\
            'GROUP BY company_name '\
            'ORDER BY COUNT(vacancies.vacancy_id) DESC;'
        columns, data = self.custom_request(sql_exec, return_data=True)
        if print_result:
            self.tables_printer(columns, data)
        return data

    def get_all_vacancies(self, print_result=True):
        sql_exec = 'SELECT companies.company_name, vacancy_name, avg_salary, vacancy_url FROM vacancies '\
            'JOIN companies USING(company_id);'
        columns, data = self.custom_request(sql_exec, return_data=True)
        if print_result:
            self.tables_printer(columns, data)
        return data

    def get_avg_salary(self, print_result=True):
        sql_exec = "SELECT AVG(avg_salary) AS average_salary FROM vacancies "\
            "WHERE avg_salary <> 0;"
        columns, data = self.custom_request(sql_exec, return_data=True)
        if not data[0][0]:
            data[0] = (0,)
        if print_result:
            self.tables_printer(columns, data)
        return data

    def get_vacancies_with_higher_salary(self, print_result=True):
        avg_salary = self.get_avg_salary(print_result=False)[0][0]
        sql_exec = "SELECT companies.company_name, vacancy_name, avg_salary, vacancy_url FROM vacancies "\
            "JOIN companies USING(company_id) "\
            f"WHERE avg_salary > {avg_salary};"
        columns, data = self.custom_request(sql_exec, return_data=True)
        if print_result:
            self.tables_printer(columns, data)
        return data

    def get_vacancies_with_keyword(self, keyword, print_result=True):
        sql_exec = "SELECT companies.company_name, vacancy_name, avg_salary, vacancy_url FROM vacancies "\
            "JOIN companies USING(company_id) "\
            f"WHERE vacancy_name LIKE '%{keyword}%';"
        columns, data = self.custom_request(sql_exec, return_data=True)
        if print_result:
            self.tables_printer(columns, data)
        return data

    def tables_printer(self, columns, data):
        if data:
            print(tabulate(data, headers=columns, tablefmt='pretty'))
        else:
            print('Нет результатов.')

    def clear_data(self):
        with open('create_tables.sql', encoding='utf-8') as file:
            sql_exec = file.read()
            self.custom_request(sql_exec)


if __name__ == '__main__':
    PostgresAPI().get_connect()
