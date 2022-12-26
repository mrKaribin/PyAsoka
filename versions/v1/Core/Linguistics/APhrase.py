from PyAsoka.Core.Linguistics.Word import Word


class APhrase:
    def __init__(self, words: list):
        self.words = words

    def __add__(self, other: Word):
        self.words.append(other)
        return self

    def __sub__(self, other: Word):
        self.words.remove(other)
        return self

    def __str__(self):
        return self.string()

    def string(self):
        result = ''
        for word in self.words:
            result += word.text + ' '
        return result.strip()

    def __contains__(self, item):
        from PyAsoka.Core.Linguistics.APhraseModel import APhraseModel
        if isinstance(item, APhraseModel):
            pass  # ToDo
