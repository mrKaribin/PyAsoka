import enum

from PyAsoka.Core.Linguistics.ANoun import ANoun, AWord
from PyAsoka.Core.Linguistics.AVerb import AVerb
from PyAsoka.Core.Linguistics.AAdjective import AAdjective


class AWordModel:
    def __init__(self, word: str = None, part_o_s: AWord.PartOfSpeech = None, aspect: AVerb.Aspect = None,
                 animacy: ANoun.Animacy = None, mood: AVerb.Mood = None, involvement: AVerb.Involvement = None,
                 transitivity: AVerb.Transitivity = None, key_number: str = None):
        self.word = word
        self.part_of_speach = part_o_s
        self.animacy = animacy
        self.aspect = aspect
        self.mood = mood
        self.involvement = involvement
        self.transitivity = transitivity
        self.genders = []
        self.numbers = []
        self.cases = []
        self.tenses = []
        self.key = True if key_number is not None else False
        self.key_number = key_number
        self.key_value = None

    def add_genders(self, *args: ANoun.Gender):
        for gender in args:
            if gender in ANoun.Gender.all:
                self.genders.append(gender)
            else:
                raise ValueError(f'Не подходящий тип данных: {gender}. Ожидалось одно из значений: {ANoun.Gender.all}')
        return self

    def add_numbers(self, *args: ANoun.Number):
        for number in args:
            if number in ANoun.Number.all:
                self.numbers.append(number)
            else:
                raise ValueError(f'Не подходящий тип данных: {number}. Ожидалось одно из значений: {ANoun.Number.all}')
        return self

    def add_cases(self, *args: ANoun.Case):
        for case in args:
            if case in ANoun.Case.all:
                self.cases.append(case)
            else:
                raise ValueError(f'Не подходящий тип данных: {case}. Ожидалось одно из значений: {ANoun.Case.all}')
        return self

    def add_tenses(self, *args: AVerb.Tense):
        for tense in args:
            if tense in AVerb.Tense.all:
                self.tenses.append(tense)
            else:
                raise ValueError(f'Не подходящий тип данных: {tense}. Ожидалось одно из значений: {AVerb.Tense.all}')
        return self

    def __eq__(self, word):
        if isinstance(word, AWord):
            self.key_value = None
            pos = AWord.PartOfSpeech

            if self.word is not None and self.word != word.normal:
                return False
            if self.part_of_speach is not None and self.part_of_speach != word.part_of_speech:
                return False

            if isinstance(word, ANoun) or isinstance(word, AAdjective):
                if len(self.cases) > 0 and word.case not in self.cases:
                    return False

            if isinstance(word, ANoun) or isinstance(word, AAdjective) or isinstance(word, AVerb):
                if len(self.genders) > 0 and word.gender not in self.genders:
                    return False
                if len(self.numbers) > 0 and word.number not in self.numbers:
                    return False

            if isinstance(word, AVerb):
                if len(self.tenses) > 0 and word.tense not in self.tenses:
                    return False

            return True
        else:
            raise ValueError(f'Не верный тип для сравнения с AWordModel: {type(word)}')
