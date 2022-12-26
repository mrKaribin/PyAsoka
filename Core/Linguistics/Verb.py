from PyAsoka.Core.Linguistics.Noun import *


class Verb(Word):

    class Number(Noun.Number):
        pass

    class Gender(Noun.Gender):
        pass

    class Person(LinguisticTags):
        First = auto()
        Second = auto()
        Third = auto()
        all = [First, Second, Third]

        @staticmethod
        def data():
            return (
                (Verb.Person.First, ('1per',), 'Первое лицо'),
                (Verb.Person.Second, ('2per',), 'Второе лицо'),
                (Verb.Person.Third, ('3per',), 'Третье лицо'),
            )

    class Aspect(LinguisticTags):
        PERFECT = auto()
        IMPERFECT = auto()
        all = [PERFECT, IMPERFECT]

        @staticmethod
        def data():
            return (
                (Verb.Aspect.PERFECT, ('perf',), 'Совершенная форма'),
                (Verb.Aspect.IMPERFECT, ('impf',), 'Несовершенная форма'),
            )

    class Tense(LinguisticTags):
        PAST = auto()
        PRESENT = auto()
        FUTURE = auto()
        all = [PAST, PRESENT, FUTURE]

        @staticmethod
        def data():
            return (
                (Verb.Tense.PAST, ('past',), 'Прошлое время'),
                (Verb.Tense.PRESENT, ('pres',), 'Настоящее время'),
                (Verb.Tense.FUTURE, ('futr',), 'Будущее время'),
            )

    class Mood(LinguisticTags):
        INDICATIVE = auto()
        IMPERATIVE = auto()
        all = [INDICATIVE, IMPERATIVE]

        @staticmethod
        def data():
            return (
                (Verb.Mood.INDICATIVE, ('indc',), 'Изъявительное наклонение'),
                (Verb.Mood.IMPERATIVE, ('impr',), 'Повелительное наклонение'),
            )

    class Involvement(LinguisticTags):
        INVOLVED = auto()
        UNINVOLVED = auto()
        all = [INVOLVED, UNINVOLVED]

        @staticmethod
        def data():
            return (
                (Verb.Involvement.INVOLVED, ('incl',), 'Включенность'),
                (Verb.Involvement.UNINVOLVED, ('excl',), 'Обособленность'),
            )

    class Transitivity(LinguisticTags):
        TRANSITIVE = auto()
        INTRANSITIVE = auto()
        all = [TRANSITIVE, INTRANSITIVE]

        @staticmethod
        def data():
            return (
                (Verb.Transitivity.TRANSITIVE, ('tran',), 'Переходный'),
                (Verb.Transitivity.INTRANSITIVE, ('intr',), 'Непереходный'),
            )

    def __init__(self, word, params):
        super().__init__(word, params)
        self.number = Verb.Number.from_pymorphy2(params.tag.number)
        self.gender = Verb.Gender.from_pymorphy2(params.tag.gender)
        self.person = Verb.Person.from_pymorphy2(params.tag.person)
        self.aspect = Verb.Aspect.from_pymorphy2(params.tag.aspect)
        self.tense = Verb.Tense.from_pymorphy2(params.tag.tense)
        self.mood = Verb.Mood.from_pymorphy2(params.tag.mood)
        self.involvement = Verb.Involvement.from_pymorphy2(params.tag.involvement)
        self.transitivity = Verb.Transitivity.from_pymorphy2(params.tag.transitivity)

    def params_to_string(self):
        return super().params_to_string() + f', {Verb.Number.to_string(self.number)}, ' \
                                            f'{Verb.Gender.to_string(self.gender)}, ' \
                                            f'{Verb.Person.to_string(self.person)}, ' \
                                            f'{Verb.Aspect.to_string(self.aspect)}, ' \
                                            f'{Verb.Tense.to_string(self.tense)}, ' \
                                            f'{Verb.Mood.to_string(self.mood)}, ' \
                                            f'{Verb.Involvement.to_string(self.involvement)}, ' \
                                            f'{Verb.Transitivity.to_string(self.transitivity)}'
