from copy import copy
from enum import Enum, auto

from PyAsoka.src.Linguistics.AWordModel import *
from PyAsoka.src.Linguistics.Phrase import Phrase


class APhraseModel:
    class Type(Enum):
        LINEAR = auto()
        NON_LINEAR = auto()
        CHOICE = auto()
        OPTIONS = auto()

    @staticmethod
    def parse(regex: str):
        import PyAsoka.src.Linguistics.APhraseModelParser as Parser
        return Parser.parse(regex)

    def __init__(self, _type: Type):
        self.type = _type
        self.components = []
        self.keys = {}
        self.coincidences = []

    def add(self, component):
        if isinstance(component, AWordModel) or isinstance(component, APhraseModel):
            self.components.append(component)
        return self

    def __eq__(self, _phrase):
        phrase = copy(_phrase)
        if isinstance(phrase, Phrase):
            self.coincidences = []
            t = APhraseModel.Type

            if self.type == t.LINEAR:
                shift = 0
                for i in range(len(self.components)):
                    if i + shift < len(phrase.words):
                        if isinstance(self.components[i], AWordModel):
                            condition = self.components[i] == phrase.words[i + shift]
                            print(f'Comparing {self.components[i].word} and {phrase.words[i + shift]}: {condition}')
                            if condition:
                                if self.components[i].key:
                                    self.keys[self.components[i].key_number] = self.components[i].key_value
                                self.coincidences.append(phrase.words[i + shift])
                            else:
                                return False

                        elif isinstance(self.components[i], APhraseModel):
                            interval = self.components[i].words_count()
                            if len(phrase.words) <= i + shift + interval:
                                if self.components[i]._type_ in (t.OPTIONS, t.CHOICE):
                                    interval = len(phrase.words) - 1 - i - shift
                                else:
                                    return False

                            fragment = Phrase(phrase.words[i + shift: i + shift + interval])
                            condition = self.components[i] == fragment
                            print(f'Comparing component and {[word.text for word in fragment.words]}: {condition}')
                            if condition:
                                self.keys = {**self.keys, **self.components[i].keys}
                                self.coincidences = [*self.coincidences, *self.components[i].coincidences]
                                shift += len(self.components[i].coincidences)
                            else:
                                return False
                    else:
                        return False
                return True

            elif self.type == t.NON_LINEAR:
                for component in self.components:
                    length = 1 if isinstance(component, AWordModel) else component.words_count()
                    component_ok = False
                    for i in range(len(phrase.words)):
                        if isinstance(component, AWordModel):
                            condition = component == phrase.words[i]
                            print(f'Comparing {component.word} and {phrase.words[i]}: {condition}')
                            if condition:
                                if component.key:
                                    self.keys[component.key_number] = component.key_value
                                self.coincidences.append(phrase.words[i])
                                phrase.words.remove(phrase.words[i])
                                component_ok = True
                                break

                        elif isinstance(component, APhraseModel):
                            if length + i <= len(phrase.words):
                                fragment = Phrase(phrase.words[i: i + length])
                            elif component.type in (t.CHOICE, t.OPTIONS):
                                fragment = Phrase(phrase.words[i: len(phrase.words)])
                            else:
                                return False

                            condition = component == fragment
                            print(f'Comparing component and {[word.text for word in fragment.words]}: {condition}')
                            if condition:
                                self.keys = {**self.keys, **component.keys}
                                self.coincidences = [*self.coincidences, *component.coincidences]
                                for word in fragment.words:
                                    phrase.words.remove(word)
                                component_ok = True
                                break

                    if not component_ok:
                        return False
                return True

            elif self.type == t.CHOICE:
                for component in self.components:
                    if isinstance(component, AWordModel):
                        for word in phrase.words:
                            condition = component == word
                            print(f'Comparing {component.word} and {word}: {condition}')
                            if condition:
                                if component.key:
                                    self.keys[component.key_number] = component.key_value
                                self.coincidences.append(word)
                                return True

                    elif isinstance(component, APhraseModel):
                        length = component.words_count()
                        for i in range(len(phrase.words) - length + 1):
                            if length + i <= len(phrase.words):
                                fragment = Phrase(phrase.words[i: i + length])
                            elif component.type in (t.CHOICE, t.OPTIONS):
                                fragment = Phrase(phrase.words[i: len(phrase.words)])
                            else:
                                return False

                            condition = component == fragment
                            print(f'Comparing component and {[word.text for word in fragment.words]}: {condition}')
                            if condition:
                                self.keys = {**self.keys, **component.keys}
                                self.coincidences = [*self.coincidences, *component.coincidences]
                                return True
                return False

        else:
            super(APhraseModel, self).__eq__(_phrase)
            # raise ValueError(f'Не верный тип для сравнения с APhraseModel: {type(phrase)}')

    def __ne__(self, other):
        return not self.__eq__(other)

    def contained(self, phrase):
        if isinstance(phrase, Phrase):
            pass  # ToDo
        else:
            raise ValueError(f'Не верный тип для поверки принадлежности с APhraseModel: {type(phrase)}')

    def words_count(self):
        t = APhraseModel.Type
        count = 0
        if self.type in (t.LINEAR, t.NON_LINEAR, t.OPTIONS):
            for component in self.components:
                if isinstance(component, AWordModel):
                    count += 1
                elif isinstance(component, APhraseModel):
                    count += component.words_count()
        elif self.type == t.CHOICE:
            for component in self.components:
                top = 0
                if isinstance(component, AWordModel):
                    top = 1
                elif isinstance(component, APhraseModel):
                    top = component.words_count()
                if top > count:
                    count = top
        return count
