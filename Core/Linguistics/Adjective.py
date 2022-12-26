from PyAsoka.Core.Linguistics.Noun import *


class Adjective(Word):

    class Gender(Noun.Gender):
        pass

    class Number(Noun.Number):
        pass

    class Case(Noun.Case):
        pass

    def __init__(self, word: str, params):
        super().__init__(word, params)
        self.number = Adjective.Number.from_pymorphy2(params.tag.number)
        self.gender = Adjective.Gender.from_pymorphy2(params.tag.gender)
        self.case = Adjective.Case.from_pymorphy2(params.tag.case)

    def params_to_string(self):
        return super().params_to_string() + f', {Adjective.Number.to_string(self.number)}, ' \
                                            f'{Adjective.Gender.to_string(self.gender)}, ' \
                                            f'{Adjective.Case.to_string(self.case)}'
