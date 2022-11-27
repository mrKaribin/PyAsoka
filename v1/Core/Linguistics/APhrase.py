from PyAsoka.Core.Linguistics.AWord import AWord


class APhrase:
    def __init__(self, words: list):
        self.words = words

    def __add__(self, other: AWord):
        self.words.append(other)
        return self

    def __sub__(self, other: AWord):
        self.words.remove(other)
        return self

    def __str__(self):
        return self.string()

    def string(self):
        result = ''
        for word in self.words:
            result += word.string + ' '
        return result.strip()

    def __contains__(self, item):
        from PyAsoka.Core.Linguistics.APhraseModel import APhraseModel
        if isinstance(item, APhraseModel):
            pass  # ToDo
