DROP TABLE IF EXISTS vacancies;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies(
    company_id INTEGER PRIMARY KEY NOT NULL,
    company_name VARCHAR(50),
    company_url VARCHAR(100)
);

CREATE TABLE vacancies(
    vacancy_id SERIAL PRIMARY KEY NOT NULL,
    vacancy_name VARCHAR(250) NOT NULL,
    avg_salary INTEGER,
    vacancy_address VARCHAR(250),
    vacancy_url VARCHAR(250),
    company_id INTEGER REFERENCES companies(company_id)
);