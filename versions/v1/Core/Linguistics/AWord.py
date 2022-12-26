from enum import Enum, auto


class LinguisticTags:
    @staticmethod
    def data():
        return set()

    @classmethod
    def from_pymorphy2(cls, arg: str):
        if arg is None:
            return None
        for part in cls.data():
            id, pmrf_id, name = part
            if arg in pmrf_id:
                return id
        return None

    @classmethod
    def to_pymorphy2(cls, value):
        if value is None:
            return None
        for part in cls.data():
            id, pmrf_id, name = part
            if value == id:
                return pmrf_id
        return None

    @classmethod
    def to_string(cls, _id):
        for part in cls.data():
            id, pmrf_id, name = part
            if _id == id:
                return name
        return None


class AWord:

    class PartOfSpeech(LinguisticTags):
        NOUN = auto()  # существительное
        VERB = auto()  # глагол
        ADJECTIVE = auto()  # прилагательное
        PARTICIPLE_ADJ = auto()  # причастие
        PARTICIPLE_VRB = auto()  # деепричастие
        ADVERB = auto()  # наречие
        NUMERAL = auto()  # числительное
        PRONOUN = auto()  # местоимение
        PREDICATIVE = auto()  # предикатив
        PREPOSITION = auto()  # предлог
        CONJUNCTION = auto()  # союз
        PARTICLE = auto()  # частица
        INTERJECTION = auto()  # междометие

        @staticmethod
        def data():
            return (
                (AWord.PartOfSpeech.NOUN, ('NOUN', ), 'Существительное'),
                (AWord.PartOfSpeech.VERB, ('VERB', 'INFN'), 'Глагол'),
                (AWord.PartOfSpeech.ADJECTIVE, ('ADJF', 'ADJS'), 'Прилагательное'),
                (AWord.PartOfSpeech.PARTICIPLE_ADJ, ('PRTF', 'PRTS'), 'Причастие'),
                (AWord.PartOfSpeech.PARTICIPLE_VRB, ('GRND', ), 'Деепричастие'),
                (AWord.PartOfSpeech.ADVERB, ('ADVB', ), 'Наречие'),
                (AWord.PartOfSpeech.NUMERAL, ('NUMR', ), 'Числительное'),
                (AWord.PartOfSpeech.PRONOUN, ('NPRO', ), 'Местоимение'),
                (AWord.PartOfSpeech.PREDICATIVE, ('PRED', ), 'Предикатив'),
                (AWord.PartOfSpeech.PREPOSITION, ('PREP', ), 'Предлог'),
                (AWord.PartOfSpeech.CONJUNCTION, ('CONJ', ), 'Союз'),
                (AWord.PartOfSpeech.PARTICLE, ('PRCL', ), 'Частица'),
                (AWord.PartOfSpeech.INTERJECTION, ('INTJ', ), 'Междометие')
            )

    def __init__(self, word: str, params):
        self.string = word
        self.params = params
        self.normal = self.params.normal_form
        self.part_of_speech = AWord.PartOfSpeech.from_pymorphy2(params.tag.POS)

    @staticmethod
    def create(word, params):
        from PyAsoka.Core.Linguistics.Noun import Noun
        from PyAsoka.Core.Linguistics.Verb import Verb
        from PyAsoka.Core.Linguistics.Adjective import Adjective
        part = AWord.PartOfSpeech

        # print(params)
        if params.tag.POS in part.to_pymorphy2(part.NOUN):
            return Noun(word, params)
        elif params.tag.POS in part.to_pymorphy2(part.VERB):
            return Verb(word, params)
        elif params.tag.POS in part.to_pymorphy2(part.ADJECTIVE):
            return Adjective(word, params)
        else:
            return AWord(word, params)

    def __str__(self):
        return self.string

    def params_to_string(self):
        return f'Слово: {self.string} :: {self.normal} :: {self.params.tag} :: {AWord.PartOfSpeech.to_string(self.part_of_speech)}'

