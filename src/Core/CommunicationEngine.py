from PyAsoka.Debug import Exceptions
from PyAsoka.src.Core.SpeechEngine import SpeechEngine, Phrase
from PyAsoka.src.Core.SpeechRecognition import SpeechRecognition
from PyAsoka.src.Core.Signal import Signal
from PyAsoka.Asoka import Asoka
from threading import Timer, Thread

import time


class PhrasesManager:
    def __init__(self):
        self._phrases_ = {}

    def append(self, phrase: Phrase):
        self._phrases_[phrase.user] = phrase

    def last(self):
        return list(self._phrases_.values())[-1]


class CommunicationEngine:
    def __init__(self, user, voice: SpeechEngine.Voices = SpeechEngine.Voices.IVONA):
        self._active_ = True
        self._listening_ = False
        self._listening_timer_ = None
        self._listening_duration_ = 300.0
        self._user_ = user

        self.speech = SpeechEngine(voice)
        self.recognition = SpeechRecognition()
        self.phrases = PhrasesManager()

        self.speaking = Signal(Phrase)
        self.listening = Signal(bool)

        self.thread = Thread(target=self.run)
        self.thread.start()

    @property
    def user(self):
        return self._user_

    @property
    def active(self):
        return self._active_

    @property
    def isListening(self):
        return self._listening_

    def say(self, arg):
        if isinstance(arg, Phrase):
            phrase = arg
            phrase.user = self._user_
        elif isinstance(arg, str):
            phrase = Phrase(arg, self._user_)
        else:
            Exceptions.UnsupportableType(arg)

        self.speech.say(phrase)
        self.phrases.append(phrase)
        phrase.started.bind(self.speaking)

    def run(self):
        from PyAsoka.src.Linguistics import APhraseModelParser as Model

        name = self._user_.name.lower()
        print(name)
        hello_model = Model.parse(f'[N {name} [C окей привет здравствуй здорово [N ты [C тут здесь]] [N добрый [C день вечер утро]]]]')
        bye_model = Model.parse(f'[C пока забудь [L до скорого]]')
        self.listening_start()
        while self._active_:
            phrase = self.recognition.listen()
            text = phrase.text()
            if text == self.phrases.last().text:
                continue

            if not self._listening_ and hello_model == phrase:
                self.say('Привет, чем займемся?')
                self.listening_start()
                continue

            if self._listening_:
                self.phrases.append(Phrase(text))

                if bye_model == phrase:
                    self.say('Если понадоблюсь, только позовите')
                    self.listening_stop()

                if False:
                    for action in self.actions:
                        if action.model == phrase:
                            self.connect_to(action.event_id, [], {'action': action.model.keys})
                            self.listening_start()
                            continue
            time.sleep(Asoka.defaultCycleDelay)

    def listening_start(self):
        if self._listening_timer_ is not None:
            self._listening_timer_.cancel()
        self._listening_ = True
        self._listening_timer_ = Timer(self._listening_duration_, self.listening_stop)
        self._listening_timer_.start()

    def listening_stop(self):
        self._listening_ = False
        self._listening_timer_ = None

    def phrase_started(self, phrase):
        self.speaking(phrase)
