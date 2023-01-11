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

    def say(self, arg):
        print('step2')
        if isinstance(arg, Phrase):
            phrase = arg
            phrase.user = self._user_
        elif isinstance(arg, str):
            phrase = Phrase(arg, self._user_)
        else:
            Exceptions.UnsupportableType(arg)

        self.speech.say(phrase)
        print('step4.1')
        self.phrases.append(phrase)
        print('step4.2')
        phrase.started.bind(self.speaking)
        print('step4.3')

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
                print('step1')
                self.say('Привет, чем займемся?')
                print('step5')
                self.listening_start()
                print('step6')
                continue

            if self._listening_:
                self.phrases.append(Phrase(text))

                if bye_model == phrase:
                    print('step1')
                    self.say('Если понадоблюсь, только позовите')
                    print('step5')
                    self.listening_stop()
                    print('step6')

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
