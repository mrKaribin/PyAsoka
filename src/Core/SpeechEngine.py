from PyAsoka.src.Core.Signal import Signal
from threading import Thread

import random
import time
import pyttsx3
import pythoncom


class Phrase:

    class Priority:
        LOW = 1
        NORMAL = 2
        HIGH = 3
        EXTREME = 4

    def __init__(self, text, user=None, priority: Priority = Priority.NORMAL):
        self.user = user
        self.text = text
        self.priority = priority

        self.started = Signal(Phrase)
        self.ended = Signal(Phrase)


class PhraseManager:
    def __init__(self):
        self._low_ = []
        self._normal_ = []
        self._high_ = []
        self._extreme_ = []
        self._map_ = {
            Phrase.Priority.LOW: self._low_,
            Phrase.Priority.NORMAL: self._normal_,
            Phrase.Priority.HIGH: self._high_,
            Phrase.Priority.EXTREME: self._extreme_
        }

    def append(self, phrase):
        self._map_[phrase.priority].append(phrase)

    def repeat(self, phrase):
        self._map_[phrase.priority].insert(0, phrase)

    def pop(self):
        if len(self._extreme_):
            return self._extreme_.pop(0)
        if len(self._high_):
            return self._high_.pop(0)
        if len(self._normal_):
            return self._normal_.pop(0)
        if len(self._low_):
            return self._low_.pop(0)

    def next(self):
        if len(self._extreme_):
            return self._extreme_[0]
        if len(self._high_):
            return self._high_[0]
        if len(self._normal_):
            return self._normal_[0]
        if len(self._low_):
            return self._low_[0]

    def size(self):
        return len(self._low_) + len(self._normal_) + len(self._high_) + len(self._extreme_)


class SpeechEngine:
    Priority = Phrase.Priority

    class Voices:
        TATYANA = 'Tatiana'
        IVONA = 'IVONA 2 Tatyana OEM'
        KATYA = 'VE_Russian_Katya_22kHz'

    def __init__(self, name=Voices.IVONA):
        self._voice_name_ = name
        self._rate_ = 100
        self._cancel_ = False
        self.engine = None
        self.thread = None
        self.current = None
        self.phrases = PhraseManager()
        self.setRate(170)

        self.thread = Thread(target=self.run)
        self.thread.start()

    def getRate(self):
        return self._rate_

    def setRate(self, percent):
        self._rate_ = percent

    def say(self, phrase: Phrase):
        print('step3')
        if self.current is not None:
            condition1 = Phrase.Priority.LOW == self.current.priority < phrase.priority
            condition2 = self.current.priority < phrase.priority == Phrase.Priority.EXTREME
            if condition1 or condition2:
                self.stop()

        self.phrases.append(phrase)
        print('step4')
        return phrase

    def stop(self):
        print('cancel')
        self._cancel_ = True

    def run(self):
        pythoncom.CoInitializeEx(0)
        while True:
            engine = pyttsx3.init()
            self.engine = engine
            voices = engine.getProperty('voices')
            for voice in voices:
                if voice.name == self._voice_name_:
                    engine.setProperty('voice', voice.id)
            engine.setProperty('rate', self._rate_)
            engine.connect('started-utterance', self.__on_start__)
            engine.connect('started-word', self.__on_word__)
            engine.connect('finished-utterance', self.__on_end__)

            while True:
                if self.phrases.size():
                    phrase = self.phrases.pop()
                    self.current = phrase
                    print(phrase.text)
                    engine.say(phrase.text, f'Phrase{random.randint(0, 1000)}')
                    engine.runAndWait()
                time.sleep(0.1)

                if self.phrases.size() and self.phrases.next().priority < Phrase.Priority.HIGH:
                    time.sleep(2)

                if self._cancel_:
                    self._cancel_ = False
                    self.current = None
                    break

            self.engine = None
            del [engine]
            time.sleep(0.2)

    def __on_start__(self, name):
        # print('start ' + name)
        self.current.started(self.current)

    def __on_word__(self, name, location, length):
        # print('word', name, location, length)
        if self._cancel_:
            # print('stop')
            self.engine.stop()

    def __on_end__(self, name, completed):
        # print('end ' + name, completed)
        if completed:
            self.current.ended(self.current)
        else:
            self.phrases.repeat(self.current)
        self.current = None
