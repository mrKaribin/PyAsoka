from PyAsoka.src.Linguistics.Word import Word


class Phrase:
    def __init__(self, words=None):
        if words is None:
            words = []

        self.words = words

    def __add__(self, other: Word):
        self.words.append(other)
        return self

    def __sub__(self, other: Word):
        self.words.remove(other)
        return self

    def __str__(self):
        return self.text()

    def text(self):
        result = ''
        for word in self.words:
            result += word.string + ' '
        return result.strip()

    def __contains__(self, item):
        from PyAsoka.src.Linguistics.APhraseModel import APhraseModel
        if isinstance(item, APhraseModel):
            pass  # ToDo

