from PyAsoka.Core.Linguistics.ANoun import *


class AAdjective(AWord):

    class Gender(ANoun.Gender):
        pass

    class Number(ANoun.Number):
        pass

    class Case(ANoun.Case):
        pass

    def __init__(self, word: str, params):
        super().__init__(word, params)
        self.number = AAdjective.Number.from_pymorphy2(params.tag.number)
        self.gender = AAdjective.Gender.from_pymorphy2(params.tag.gender)
        self.case = AAdjective.Case.from_pymorphy2(params.tag.case)

    def params_to_string(self):
        return super().params_to_string() + f', {AAdjective.Number.to_string(self.number)}, ' \
                                            f'{AAdjective.Gender.to_string(self.gender)}, ' \
                                            f'{AAdjective.Case.to_string(self.case)}'
