class CompanyNameNotChosen(Exception):
    def __init__(self, exc_text='Вы не вписали компанию для поиска'):
        super().__init__(exc_text)


class CompanyFormatError(Exception):
    def __init__(self, exc_text='Неверный формат компании'):
        super().__init__(exc_text)
