import os
import sys
import requests
import re
from exceptions import CompanyNameNotChosen, CompanyFormatError
from vacancy import Vacancy


class HeadHunterAPI:
    def __init__(self, debug=False):
        self.debug = debug
        self.currency_dict = {}

    def get_company(self, company=''):
        url = "https://api.hh.ru/employers"
        params = {
            "area": 1,  # Specify the desired area ID (1 is Moscow)
            "page": 0,  # Specify the page number
            "per_page": 100,  # Number of companies per page
            "host": 'hh.ru'
        }
        # Если ищем по ключевым словам
        if company:
            params['text'] = company
        else:
            raise CompanyNameNotChosen()

        page_data = self.get_page_data(url, params=params)
        company_index = 0
        if self.debug:
            from pprint import pprint
            pprint(page_data)

        # Если нашлось несколько компаний
        if len(page_data['items']) == 0:
            print('Компания не найдена.')
            return
        elif len(page_data['items']) > 1:
            companies_string = '\n'.join([f'{index+1}: {company["name"]}'
                                          for index, company in enumerate(page_data['items'])])
            message = 'Нашлись несколько компаний, пожалуйста укажите нужную компанию:'

            while True:
                try:
                    # Вычитаем 1 т.к. индексы с нуля
                    company_index = int(input(
                        f'{message}\n{companies_string}\n-->').strip()) - 1
                    break
                except ValueError:
                    message = 'Неправильный формат ответа, убедитесь что вводите числовое значение:'

        return page_data['items'][company_index]

    def get_company_vacancies(self, company: dict):
        params = {
            "per_page": 100,  # Number of companies per page
        }
        vacancies = []

        if company.get('vacancies_url'):
            for page in range(20):
                params['page'] = page
                company_vacancies = self.get_page_data(
                    company.get('vacancies_url'),
                    params=params)
                if not company_vacancies:
                    break
                elif company_vacancies.get('items'):
                    vacancies.extend(company_vacancies['items'])
                else:
                    break
            return vacancies
        else:
            raise CompanyFormatError()

    def parse_vacancies_data(self, vacancies):
        for vacancy in vacancies:
            vacancy_name = vacancy.get('name')

            if vacancy.get('salary'):
                if vacancy['salary'].get('currency') == 'RUR':
                    # Если в данных стоит None, то автоматическая замена dict.get не сработает
                    salary_from = 0
                    salary_to = 0
                    if vacancy['salary'].get('from'):
                        salary_from = vacancy.get(
                            'salary', {}).get('from')
                    if vacancy['salary'].get('to'):
                        salary_to = vacancy.get(
                            'salary', {}).get('to')
                else:
                    salary_from, salary_to = self.currency_to_rub(
                        vacancy['salary'])
            else:
                salary_from, salary_to = 0, 0

            address = (vacancy.get('address') or {}).get('raw', 'Не указан')
            url = vacancy['url']
            company_id = vacancy['employer']['id']

            Vacancy(vacancy_name, salary_from,
                    salary_to, address, url, company_id)

    def get_page_data(self, url, params={}, headers={}, retry_num=3):

        for _ in range(retry_num):
            req = requests.get(url, headers=headers, params=params)
            if req.status_code == 200:
                data = req.json()
                req.close()
                return data
            else:
                continue
        else:
            print(f'Request failed for {retry_num} times. Abandon.')

    def currency_to_rub(self, salary):
        if not self.currency_dict:
            resp = requests.get('https://api.hh.ru/dictionaries').json()
            for cur in resp['currency']:
                self.currency_dict[cur['code']] = cur['rate']
        rub_from = 0
        rub_to = 0
        if salary.get('from'):
            rub_from = salary.get('from')\
                // self.currency_dict[salary['currency']]
        if salary.get('to'):
            rub_to = salary.get('to') // self.currency_dict[salary['currency']]

        return rub_from, rub_to


hh_api = HeadHunterAPI()

if __name__ == '__main__':
    from pprint import pprint
    # sys.path.insert(0,
    #                 os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    hh_api = HeadHunterAPI(debug=True)
    company = hh_api.get_company('CoMagic')
    # company = hh_api.get_company('Yandex')
    # pprint(company)
    # company_vacancies = hh_api.get_company_vacancies(company)
    # pprint(company_vacancies[0])
    # hh_api.parse_vacancies_data(company_vacancies)
