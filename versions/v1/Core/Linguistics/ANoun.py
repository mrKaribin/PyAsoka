from PyAsoka.Core.Linguistics.AWord import *


class ANoun(AWord):

    class Number(LinguisticTags):
        SINGULAR = auto()
        PLURAL = auto()
        FIXED = auto()
        all = [SINGULAR, PLURAL, FIXED]

        @staticmethod
        def data():
            return (
                (ANoun.Number.SINGULAR, ('sing', ), 'Единственное число'),
                (ANoun.Number.PLURAL, ('plur', ), 'Множественное число'),
                (ANoun.Number.SINGULAR, ('Fixd', ), 'Неизменяемое число')
            )

    class Gender(LinguisticTags):
        MASCULINE = auto()
        FEMININE = auto()
        NEUTRAL = auto()
        GENERAL = auto()
        all = [MASCULINE, FEMININE, NEUTRAL, GENERAL]

        @staticmethod
        def data():
            return (
                (ANoun.Gender.MASCULINE, ('masc', ), 'Мужской род'),
                (ANoun.Gender.FEMININE, ('femn', ), 'Женский род'),
                (ANoun.Gender.NEUTRAL, ('neut', ), 'Средний род'),
                (ANoun.Gender.MASCULINE, ('Ms-f', 'GNdr'), 'Общий род'),
            )

    class Case(LinguisticTags):
        NOMINATIVE = auto()
        GENITIVE = auto()
        DATIVE = auto()
        ACCUSATIVE = auto()
        INSTRUMENTAL = auto()
        PREPOSITIONAL = auto()
        all = [NOMINATIVE, GENITIVE, DATIVE, ACCUSATIVE, INSTRUMENTAL, PREPOSITIONAL]

        @staticmethod
        def data():
            return (
                (ANoun.Case.NOMINATIVE, ('nomn', ), 'Именительный падеж'),
                (ANoun.Case.GENITIVE, ('gent', 'gen1', 'gen2'), 'Родительный падеж'),
                (ANoun.Case.DATIVE, ('datv', ), 'Дательный падеж'),
                (ANoun.Case.ACCUSATIVE, ('accs', 'acc2'), 'Винительный падеж'),
                (ANoun.Case.INSTRUMENTAL, ('ablt', ), 'Творительный падеж'),
                (ANoun.Case.PREPOSITIONAL, ('loct', 'loc1', 'loc2'), 'Предложный падеж'),
            )

    class Animacy(LinguisticTags):
        ANIMATE = auto()
        INANIMATE = auto()
        all = [ANIMATE, INANIMATE]

        @staticmethod
        def data():
            return (
                (ANoun.Animacy.ANIMATE, ('anim', ), 'Одушевленное'),
                (ANoun.Animacy.INANIMATE, ('inan', ), 'Неодушевленное'),
            )

    def __init__(self, word: str, params):
        super().__init__(word, params)
        self.number = ANoun.Number.from_pymorphy2(params.tag.number)
        self.gender = ANoun.Gender.from_pymorphy2(params.tag.gender)
        self.case = ANoun.Case.from_pymorphy2(params.tag.case)
        self.animate = ANoun.Animacy.from_pymorphy2(params.tag.animacy)

    def params_to_string(self):
        return super().params_to_string() + f', {ANoun.Number.to_string(self.number)}, ' \
                                            f'{ANoun.Gender.to_string(self.gender)}, ' \
                                            f'{ANoun.Case.to_string(self.case)}, ' \
                                            f'{ANoun.Animacy.to_string(self.animate)}'

