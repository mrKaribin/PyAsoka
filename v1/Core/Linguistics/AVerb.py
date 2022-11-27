from PyAsoka.Core.Linguistics.ANoun import *


class AVerb(AWord):

    class Number(ANoun.Number):
        pass

    class Gender(ANoun.Gender):
        pass

    class Person(LinguisticTags):
        First = auto()
        Second = auto()
        Third = auto()
        all = [First, Second, Third]

        @staticmethod
        def data():
            return (
                (AVerb.Person.First, ('1per', ), 'Первое лицо'),
                (AVerb.Person.Second, ('2per', ), 'Второе лицо'),
                (AVerb.Person.Third, ('3per', ), 'Третье лицо'),
            )

    class Aspect(LinguisticTags):
        PERFECT = auto()
        IMPERFECT = auto()
        all = [PERFECT, IMPERFECT]

        @staticmethod
        def data():
            return (
                (AVerb.Aspect.PERFECT, ('perf', ), 'Совершенная форма'),
                (AVerb.Aspect.IMPERFECT, ('impf', ), 'Несовершенная форма'),
            )

    class Tense(LinguisticTags):
        PAST = auto()
        PRESENT = auto()
        FUTURE = auto()
        all = [PAST, PRESENT, FUTURE]

        @staticmethod
        def data():
            return (
                (AVerb.Tense.PAST, ('past', ), 'Прошлое время'),
                (AVerb.Tense.PRESENT, ('pres', ), 'Настоящее время'),
                (AVerb.Tense.FUTURE, ('futr', ), 'Будущее время'),
            )

    class Mood(LinguisticTags):
        INDICATIVE = auto()
        IMPERATIVE = auto()
        all = [INDICATIVE, IMPERATIVE]

        @staticmethod
        def data():
            return (
                (AVerb.Mood.INDICATIVE, ('indc', ), 'Изъявительное наклонение'),
                (AVerb.Mood.IMPERATIVE, ('impr', ), 'Повелительное наклонение'),
            )

    class Involvement(LinguisticTags):
        INVOLVED = auto()
        UNINVOLVED = auto()
        all = [INVOLVED, UNINVOLVED]

        @staticmethod
        def data():
            return (
                (AVerb.Involvement.INVOLVED, ('incl', ), 'Включенность'),
                (AVerb.Involvement.UNINVOLVED, ('excl', ), 'Обособленность'),
            )

    class Transitivity(LinguisticTags):
        TRANSITIVE = auto()
        INTRANSITIVE = auto()
        all = [TRANSITIVE, INTRANSITIVE]

        @staticmethod
        def data():
            return (
                (AVerb.Transitivity.TRANSITIVE, ('tran', ), 'Переходный'),
                (AVerb.Transitivity.INTRANSITIVE, ('intr', ), 'Непереходный'),
            )

    def __init__(self, word, params):
        super().__init__(word, params)
        self.number = AVerb.Number.from_pymorphy2(params.tag.number)
        self.gender = AVerb.Gender.from_pymorphy2(params.tag.gender)
        self.person = AVerb.Person.from_pymorphy2(params.tag.person)
        self.aspect = AVerb.Aspect.from_pymorphy2(params.tag.aspect)
        self.tense = AVerb.Tense.from_pymorphy2(params.tag.tense)
        self.mood = AVerb.Mood.from_pymorphy2(params.tag.mood)
        self.involvement = AVerb.Involvement.from_pymorphy2(params.tag.involvement)
        self.transitivity = AVerb.Transitivity.from_pymorphy2(params.tag.transitivity)

    def params_to_string(self):
        return super().params_to_string() + f', {AVerb.Number.to_string(self.number)}, ' \
                                            f'{AVerb.Gender.to_string(self.gender)}, ' \
                                            f'{AVerb.Person.to_string(self.person)}, ' \
                                            f'{AVerb.Aspect.to_string(self.aspect)}, ' \
                                            f'{AVerb.Tense.to_string(self.tense)}, ' \
                                            f'{AVerb.Mood.to_string(self.mood)}, ' \
                                            f'{AVerb.Involvement.to_string(self.involvement)}, ' \
                                            f'{AVerb.Transitivity.to_string(self.transitivity)}'
