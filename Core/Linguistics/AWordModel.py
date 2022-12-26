import enum

from PyAsoka.Core.Linguistics.Noun import Noun, Word
from PyAsoka.Core.Linguistics.Verb import Verb
from PyAsoka.Core.Linguistics.Adjective import Adjective


class AWordModel:
    def __init__(self, word: str = None, part_o_s: Word.PartOfSpeech = None, aspect: Verb.Aspect = None,
                 animacy: Noun.Animacy = None, mood: Verb.Mood = None, involvement: Verb.Involvement = None,
                 transitivity: Verb.Transitivity = None, key_number: str = None):
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

    def add_genders(self, *args: Noun.Gender):
        for gender in args:
            if gender in Noun.Gender.all:
                self.genders.append(gender)
            else:
                raise ValueError(f'Не подходящий тип данных: {gender}. Ожидалось одно из значений: {Noun.Gender.all}')
        return self

    def add_numbers(self, *args: Noun.Number):
        for number in args:
            if number in Noun.Number.all:
                self.numbers.append(number)
            else:
                raise ValueError(f'Не подходящий тип данных: {number}. Ожидалось одно из значений: {Noun.Number.all}')
        return self

    def add_cases(self, *args: Noun.Case):
        for case in args:
            if case in Noun.Case.all:
                self.cases.append(case)
            else:
                raise ValueError(f'Не подходящий тип данных: {case}. Ожидалось одно из значений: {Noun.Case.all}')
        return self

    def add_tenses(self, *args: Verb.Tense):
        for tense in args:
            if tense in Verb.Tense.all:
                self.tenses.append(tense)
            else:
                raise ValueError(f'Не подходящий тип данных: {tense}. Ожидалось одно из значений: {Verb.Tense.all}')
        return self

    def __eq__(self, word):
        if isinstance(word, Word):
            self.key_value = None
            pos = Word.PartOfSpeech

            if self.word is not None and self.word != word.normal:
                return False
            if self.part_of_speach is not None and self.part_of_speach != word.part_of_speech:
                return False

            if isinstance(word, Noun) or isinstance(word, Adjective):
                if len(self.cases) > 0 and word.case not in self.cases:
                    return False

            if isinstance(word, Noun) or isinstance(word, Adjective) or isinstance(word, Verb):
                if len(self.genders) > 0 and word.gender not in self.genders:
                    return False
                if len(self.numbers) > 0 and word.number not in self.numbers:
                    return False

            if isinstance(word, Verb):
                if len(self.tenses) > 0 and word.tense not in self.tenses:
                    return False

            return True
        else:
            raise ValueError(f'Не верный тип для сравнения с AWordModel: {type(word)}')
