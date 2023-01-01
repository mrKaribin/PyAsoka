from enum import auto


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


class Word:

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
                (Word.PartOfSpeech.NOUN, ('NOUN',), 'Существительное'),
                (Word.PartOfSpeech.VERB, ('VERB', 'INFN'), 'Глагол'),
                (Word.PartOfSpeech.ADJECTIVE, ('ADJF', 'ADJS'), 'Прилагательное'),
                (Word.PartOfSpeech.PARTICIPLE_ADJ, ('PRTF', 'PRTS'), 'Причастие'),
                (Word.PartOfSpeech.PARTICIPLE_VRB, ('GRND',), 'Деепричастие'),
                (Word.PartOfSpeech.ADVERB, ('ADVB',), 'Наречие'),
                (Word.PartOfSpeech.NUMERAL, ('NUMR',), 'Числительное'),
                (Word.PartOfSpeech.PRONOUN, ('NPRO',), 'Местоимение'),
                (Word.PartOfSpeech.PREDICATIVE, ('PRED',), 'Предикатив'),
                (Word.PartOfSpeech.PREPOSITION, ('PREP',), 'Предлог'),
                (Word.PartOfSpeech.CONJUNCTION, ('CONJ',), 'Союз'),
                (Word.PartOfSpeech.PARTICLE, ('PRCL',), 'Частица'),
                (Word.PartOfSpeech.INTERJECTION, ('INTJ',), 'Междометие')
            )

    def __init__(self, word: str, params):
        self.string = word
        self.params = params
        self.normal = self.params.normal_form
        self.part_of_speech = Word.PartOfSpeech.from_pymorphy2(params.tag.POS)

    @staticmethod
    def create(word, params):
        from PyAsoka.src.Linguistics.Noun import Noun
        from PyAsoka.src.Linguistics.Verb import Verb
        from PyAsoka.src.Linguistics.Adjective import Adjective
        part = Word.PartOfSpeech

        # print(params)
        if params.tag.POS in part.to_pymorphy2(part.NOUN):
            return Noun(word, params)
        elif params.tag.POS in part.to_pymorphy2(part.VERB):
            return Verb(word, params)
        elif params.tag.POS in part.to_pymorphy2(part.ADJECTIVE):
            return Adjective(word, params)
        else:
            return Word(word, params)

    def __str__(self):
        return self.string

    def params_to_string(self):
        return f'Слово: {self.string} :: {self.normal} :: {self.params.tag} :: {Word.PartOfSpeech.to_string(self.part_of_speech)}'

