from PyAsoka.src.Linguistics.Word import *


class Noun(Word):

    class Number(LinguisticTags):
        SINGULAR = auto()
        PLURAL = auto()
        FIXED = auto()
        all = [SINGULAR, PLURAL, FIXED]

        @staticmethod
        def data():
            return (
                (Noun.Number.SINGULAR, ('sing',), 'Единственное число'),
                (Noun.Number.PLURAL, ('plur',), 'Множественное число'),
                (Noun.Number.SINGULAR, ('Fixd',), 'Неизменяемое число')
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
                (Noun.Gender.MASCULINE, ('masc',), 'Мужской род'),
                (Noun.Gender.FEMININE, ('femn',), 'Женский род'),
                (Noun.Gender.NEUTRAL, ('neut',), 'Средний род'),
                (Noun.Gender.MASCULINE, ('Ms-f', 'GNdr'), 'Общий род'),
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
                (Noun.Case.NOMINATIVE, ('nomn',), 'Именительный падеж'),
                (Noun.Case.GENITIVE, ('gent', 'gen1', 'gen2'), 'Родительный падеж'),
                (Noun.Case.DATIVE, ('datv',), 'Дательный падеж'),
                (Noun.Case.ACCUSATIVE, ('accs', 'acc2'), 'Винительный падеж'),
                (Noun.Case.INSTRUMENTAL, ('ablt',), 'Творительный падеж'),
                (Noun.Case.PREPOSITIONAL, ('loct', 'loc1', 'loc2'), 'Предложный падеж'),
            )

    class Animacy(LinguisticTags):
        ANIMATE = auto()
        INANIMATE = auto()
        all = [ANIMATE, INANIMATE]

        @staticmethod
        def data():
            return (
                (Noun.Animacy.ANIMATE, ('anim',), 'Одушевленное'),
                (Noun.Animacy.INANIMATE, ('inan',), 'Неодушевленное'),
            )

    def __init__(self, word: str, params):
        super().__init__(word, params)
        self.number = Noun.Number.from_pymorphy2(params.tag.number)
        self.gender = Noun.Gender.from_pymorphy2(params.tag.gender)
        self.case = Noun.Case.from_pymorphy2(params.tag.case)
        self.animate = Noun.Animacy.from_pymorphy2(params.tag.animacy)

    def params_to_string(self):
        return super().params_to_string() + f', {Noun.Number.to_string(self.number)}, ' \
                                            f'{Noun.Gender.to_string(self.gender)}, ' \
                                            f'{Noun.Case.to_string(self.case)}, ' \
                                            f'{Noun.Animacy.to_string(self.animate)}'

