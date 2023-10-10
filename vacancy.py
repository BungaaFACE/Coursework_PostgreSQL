class Vacancy:
    all_vacancies = []

    def __init__(self, vacancy_name, salary_from, salary_to, address, url, company_id):

        self.vacancy_name = vacancy_name
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.vacancy_address = address
        self.vacancy_url = url
        self.company_id = company_id
        Vacancy.all_vacancies.append(self)

    @property
    def avg_salary(self):
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) // 2
        elif self.salary_from:
            return self.salary_from
        elif self.salary_to:
            return self.salary_to
        else:
            return 0

    @classmethod
    def clear_vacancies(cls):
        cls.all_vacancies.clear()
