from hh_api import hh_api
from postgres_api import PostgresAPI


def debug_companies():
    for company in ['CoMagic', 'тинькофф', 'несуществующая компания']:
        yield company


class MainMenuCaller:
    def __init__(self, debug):
        self.main_menu = \
            '\n'\
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'\
            '1. Поиск вакансий по компании\n'\
            '2. Вывести количество вакансий на добавленные компании\n'\
            '3. Вывести полный список вакансий\n'\
            '4. Вывести среднюю зарплату по найденным вакансиям\n'\
            '5. Вывести вакансии с зарплатой выше средней\n'\
            '6. Поиск по названию вакансии\n'\
            '7. Очистить все загруженные данные\n'\
            '0. Выход\n'\
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        self.main_menu_calls = {
            '1': self.get_company_vacancies,
            '2': self.get_companies_and_vacancies_count,
            '3': self.get_all_vacancies,
            '4': self.get_avg_salary,
            '5': self.get_vacancies_with_higher_salary,
            '6': self.search_vacancy_name,
            '7': self.clear_all_data,
            '0': self.exit_programm
        }

        self.debug = debug
        self.debug_companies = debug_companies()

    def get_company_vacancies(self):
        if self.debug:
            company_name = next(self.debug_companies)
            print('Введите название компании для поиска:\n-->')
            print(f'-->{company_name}')
        else:
            company_name = input('Введите название компании для поиска:\n-->')

        # HeadHunter
        company = hh_api.get_company(company_name)
        company_vacancies = hh_api.get_company_vacancies(company)
        hh_api.parse_vacancies_data(company_vacancies)

        # PostgeSQL
        with PostgresAPI() as sql:
            if sql.insert_company(company):
                sql.insert_list_of_vacancies()
                print(
                    f'Добавлены {len(company_vacancies)} вакансий компании {company["name"]}')

    def get_companies_and_vacancies_count(self):
        with PostgresAPI() as sql:
            sql.get_companies_and_vacancies_count()

    def get_all_vacancies(self):
        with PostgresAPI() as sql:
            sql.get_all_vacancies()

    def get_avg_salary(self):
        with PostgresAPI() as sql:
            sql.get_avg_salary()

    def get_vacancies_with_higher_salary(self):
        with PostgresAPI() as sql:
            sql.get_vacancies_with_higher_salary()

    def search_vacancy_name(self):
        keyword = input('Введите ключевое слово для поиска по вакансиям:\n-->')
        with PostgresAPI() as sql:
            sql.get_vacancies_with_keyword(keyword)

    def clear_all_data(self):
        with PostgresAPI() as sql:
            sql.clear_data()
        print('Очищено.')

    def exit_programm(self):
        print('Спасибо за использование программы! Bye-Bye!')
        exit()

    def start_programm(self):
        while True:
            menu_choice = input(self.main_menu+'\n-->')
            if menu_choice in self.main_menu_calls:
                self.main_menu_calls[menu_choice]()
            else:
                print('Такого пункта меню нет :(')


if __name__ == '__main__':
    MainMenuCaller(debug=False).start_programm()
