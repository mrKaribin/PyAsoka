from PyAsoka.src.Core.Object import Object
from PyAsoka.src.Linguistics.Phrase import Phrase
from PyAsoka.src.Core.User import User
from PyAsoka.src.Instruments.Timepoint import Timepoint


class ConversationPhrase(Phrase):
    def __init__(self, user: User, words: list | None):
        super().__init__(words)
        self.user = user
        self.timepoint = Timepoint.now()


class Conversation:
    def __init__(self):
        self.phrases = []

    def addPhrase(self, user: User, phrase: Phrase):
        # self.phrases.append(ConversationPhrase(user, phrase.words))
        pass

    def lastPhrase(self):
        if len(self.phrases) > 0:
            return self.phrases[len(self.phrases) - 1]
        else:
            return None

    def lastPhraseByUser(self, user: User):
        for i in range(len(self.phrases) - 1, 0, -1):
            if self.phrases[i].user == user:
                return self.phrases[i]
        return None

    def duration(self):
        pass


class ConversationEngine(Object):
    def __init__(self):
        super().__init__()
        self._conversation_ = Conversation()
        self.isDialog = True

    @property
    def conversation(self):
        return self._conversation_

    def addPhrase(self, user: User, phrase: Phrase):
        self.conversation.addPhrase(user, phrase)

    def lastPhrase(self):
        return self.conversation.lastPhrase()

    def lastPhraseByUser(self, user: User):
        return self.conversation.lastPhraseByUser(user)

    def endConversation(self):
        self._conversation_ = Conversation()

    def spokePhrase(self, phrase):
        from PyAsoka.src.Core.Core import core
        phrase = core().communication.recognition.parsePhrase(phrase.text)
        user = core().communication.user
        self.addPhrase(user, phrase)
        print('Говорю: ', phrase.text())

    def recognizedPhrase(self, phrase: Phrase):
        from PyAsoka.src.Core.Core import core, Core
        from PyAsoka.src.Logic.LogicObject import LogicObject, LogicFunction, LogicParameter
        print('Распознано: ', phrase.text())

        name = core().communication.user.name.lower()
        models = Core.PhraseModels
        if not self.isDialog and models.User.hello == phrase:
            self.isDialog = True

        elif self.isDialog and models.User.bye == phrase:
            self.isDialog = False

        elif self.isDialog:
            for obj in core().objects.list():
                if isinstance(obj, LogicObject):
                    for function in obj.functions:
                        if isinstance(function, LogicFunction) and function.model == phrase:
                            function.call.emit([], {'logic': LogicParameter(phrase, function)})
