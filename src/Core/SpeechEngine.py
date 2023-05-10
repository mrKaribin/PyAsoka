from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Debug.Exceptions import Exceptions

from threading import Thread
from enum import IntEnum

import time
import torch
import pyaudio
import wave
import os


class Phrase(Object):
    started = Signal()
    finished = Signal()

    class Priority(IntEnum):
        LOW = 1
        NORMAL = 2
        HIGH = 3
        EXTREME = 4

    def __init__(self, text, user=None, priority: Priority = Priority.NORMAL):
        super().__init__()
        self.user = user
        self.text = text
        self.priority = priority
        self.soundPath = None


class PhraseManager:
    def __init__(self):
        self._low_ = []
        self._normal_ = []
        self._high_ = []
        self._extreme_ = []
        self._unprocessed_ = {
            Phrase.Priority.LOW: [],
            Phrase.Priority.NORMAL: [],
            Phrase.Priority.HIGH: [],
            Phrase.Priority.EXTREME: []
        }
        self._map_ = {
            Phrase.Priority.LOW: self._low_,
            Phrase.Priority.NORMAL: self._normal_,
            Phrase.Priority.HIGH: self._high_,
            Phrase.Priority.EXTREME: self._extreme_
        }

    def append(self, phrase: Phrase):
        if isinstance(phrase, Phrase):
            self._map_[phrase.priority].append(phrase)
            self._unprocessed_[phrase.priority].append(phrase)
        else:
            raise Exceptions.UnsupportableType(phrase)

    def repeat(self, phrase):
        self._map_[phrase.priority].insert(0, phrase)

    def pop(self) -> Phrase | bool:
        if len(self._extreme_):
            return self._extreme_.pop(0)
        elif len(self._high_):
            return self._high_.pop(0)
        elif len(self._normal_):
            return self._normal_.pop(0)
        elif len(self._low_):
            return self._low_.pop(0)
        else:
            return False

    def popUnprocessed(self) -> Phrase | bool:
        if len(self._unprocessed_[Phrase.Priority.EXTREME]):
            return self._unprocessed_[Phrase.Priority.EXTREME].pop(0)
        elif len(self._unprocessed_[Phrase.Priority.HIGH]):
            return self._unprocessed_[Phrase.Priority.HIGH].pop(0)
        elif len(self._unprocessed_[Phrase.Priority.NORMAL]):
            return self._unprocessed_[Phrase.Priority.NORMAL].pop(0)
        elif len(self._unprocessed_[Phrase.Priority.LOW]):
            return self._unprocessed_[Phrase.Priority.LOW].pop(0)
        else:
            return False

    def next(self):
        if len(self._extreme_):
            return self._extreme_[0]
        elif len(self._high_):
            return self._high_[0]
        elif len(self._normal_):
            return self._normal_[0]
        elif len(self._low_):
            return self._low_[0]
        else:
            return False

    def size(self):
        return len(self._low_) + len(self._normal_) + len(self._high_) + len(self._extreme_)


class SpeechEngine(Object):
    speakingStarted = Signal(Phrase)
    speakingFinished = Signal(Phrase)

    Priority = Phrase.Priority

    class Voices:
        BAYA = 'baya'
        TATYANA = 'Tatiana'
        IVONA = 'IVONA 2 Tatyana OEM'
        KATYA = 'VE_Russian_Katya_22kHz'

    def __init__(self, name=Voices.BAYA):
        super().__init__()
        self._voice_name_ = SpeechEngine.Voices.BAYA
        self._rate_ = 100
        self._current_ = None
        self._cancel_ = False
        self._thread_ = None
        self._model_ = None
        self._phrases_ = PhraseManager()

        from PyAsoka.Asoka import Asoka
        for i in range(1, 100):
            filepath = Asoka.Project.Path.Media.Sounds() + f'\\phrase{i}.wav'
            if os.path.exists(filepath):
                os.remove(filepath)

        self._thread_ = Thread(target=self.run)
        self._thread_.start()
        self._tts_thread_ = Thread(target=self.tts_run)
        self._tts_thread_.start()

    @property
    def rate(self):
        return self._rate_

    @rate.setter
    def rate(self, percent):
        self._rate_ = percent

    @property
    def current(self):
        return self._current_

    @property
    def phrases(self):
        return self._phrases_

    @property
    def model(self):
        return self._model_

    def say(self, phrase: Phrase):
        if isinstance(phrase, str):
            phrase = Phrase(phrase)

        if self.current is not None:
            condition1 = Phrase.Priority.LOW == self.current.priority < phrase.priority
            condition2 = self.current.priority < phrase.priority == Phrase.Priority.EXTREME
            if condition1 or condition2:
                self.stop()

        self.phrases.append(phrase)
        return phrase

    def stop(self):
        if self.current is not None:
            self._cancel_ = True

    def tts_run(self):
        from PyAsoka.Asoka import Asoka
        while True:
            if (phrase := self.phrases.popUnprocessed()) is not False and phrase.soundPath is None:
                path = Asoka.Project.Path.Asoka.Models() + '\\model.pt'
                self._model_ = torch.package.PackageImporter(path).load_pickle("tts_models", "model")
                self.model.to(torch.device('cpu'))
                self.model.save_wav(text=phrase.text,
                                    speaker=self._voice_name_,
                                    sample_rate=48000)
                self._model_ = None

                filepath = ''
                for i in range(1, 100):
                    filepath = Asoka.Project.Path.Media.Sounds() + f'\\phrase{i}.wav'
                    if not os.path.exists(filepath):
                        break
                os.replace(Asoka.Project.Path.Home() + '\\test.wav', filepath)
                phrase.soundPath = filepath

            time.sleep(Asoka.defaultCycleDelay)

    def run(self):
        from PyAsoka.Asoka import Asoka
        while True:
            if (phrase := self.phrases.next()) is not False and phrase.soundPath is not None:
                phrase = self.phrases.pop()
                self.__on_start__(phrase)
                wavefile = wave.open(phrase.soundPath, 'rb')
                chunk = 1024
                portaudio = pyaudio.PyAudio()
                stream = portaudio.open(format=portaudio.get_format_from_width(wavefile.getsampwidth()),
                                        channels=wavefile.getnchannels(),
                                        rate=wavefile.getframerate(),
                                        output=True)

                data = wavefile.readframes(chunk)
                while data != b'':
                    if self._cancel_:
                        break
                    stream.write(data)
                    data = wavefile.readframes(chunk)

                stream.close()
                portaudio.terminate()
                wavefile.close()
                if not self._cancel_:
                    if os.path.exists(phrase.soundPath):
                        os.remove(phrase.soundPath)
                    phrase.soundPath = None
                    self.__on_end__()
                else:
                    self._cancel_ = False
                    time.sleep(1)

            time.sleep(Asoka.defaultCycleDelay)

    def __on_start__(self, phrase):
        self._current_ = phrase
        self.current.started.emit()
        self.speakingStarted.emit(self.current)

    def __on_end__(self):
        self.current.finished.emit()
        self.speakingFinished.emit(self.current)
        self._current_ = None
