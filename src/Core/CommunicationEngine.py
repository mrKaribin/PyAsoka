from PyAsoka.Debug import Exceptions
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Core.SpeechEngine import SpeechEngine, Phrase
from PyAsoka.src.Core.SpeechRecognition import SpeechRecognition
from PyAsoka.src.Core.ConversationEngine import ConversationEngine
from threading import Timer, Thread

import time


class CommunicationEngine(Object):
    recognized = Signal(Phrase)

    def __init__(self, user, voice: SpeechEngine.Voices, conversation_engine: type):
        super().__init__()
        self._active_ = True
        self._listening_ = True
        self._user_ = user

        self._speech_ = SpeechEngine(voice)
        self._recognition_ = SpeechRecognition()
        self._conversation_ = conversation_engine()
        if not isinstance(self._conversation_, ConversationEngine):
            raise Exception('CommunicationEngine: класс-управляющий беседы не унаследован от ConversationEngine')

        self.speech.speakingFinished.connect(self.conversation.spokePhrase)
        self.speech.speakingStarted.connect(self.recognition.stopListening)
        self.speech.speakingFinished.connect(self.recognition.startListening)
        self.recognition.recognized.connect(self.conversation.recognizedPhrase)

    @property
    def user(self):
        return self._user_

    @property
    def active(self):
        return self._active_

    @property
    def isListening(self):
        return self._listening_

    @property
    def speech(self) -> SpeechEngine:
        return self._speech_

    @property
    def recognition(self) -> SpeechRecognition:
        return self._recognition_

    @property
    def conversation(self) -> ConversationEngine:
        return self._conversation_

    def say(self, arg):
        if isinstance(arg, Phrase):
            phrase = arg
            phrase.user = self._user_
        elif isinstance(arg, str):
            phrase = Phrase(arg, self._user_)
        else:
            Exceptions.UnsupportableType(arg)
            return

        return self.speech.say(phrase)
