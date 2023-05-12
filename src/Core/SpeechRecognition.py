from PyAsoka.src.Linguistics.Phrase import Phrase
from PyAsoka.src.Linguistics.Word import Word
from PyAsoka.src.Core.Object import Object, Signal

from threading import Thread

import pyaudio
import json
import time


class SpeechRecModel:
    def __init__(self, path, lang: 'Asoka.Language'):
        from vosk import Model
        self.language = lang
        self._model_ = Model(path)

    def __call__(self, *args, **kwargs):
        return self._model_


class SpeechRecognition(Object):
    recognized = Signal(Phrase)

    class Models:
        PERFORMANCE = 'PyAsoka/models/vosk-model-small-ru-0.22'
        QUALITY = 'PyAsoka/models/vosk-model-ru-0.42'

    def __init__(self, model: SpeechRecModel = None):
        super().__init__()
        from PyAsoka.Asoka import Asoka
        if model is None:
            path = self.Models.PERFORMANCE
            print(path)
            model = SpeechRecModel(path, Asoka.Language.RUSSIAN)
        self._listening_ = True
        self.chunk = 8000
        self.rate = 16000
        self.model = model
        self.rec = None
        self.stream = None
        self.analyzer = None
        self.ready = False

        self.loaderThread = Thread(target=self.loadAnalyzer)
        self.loaderThread.start()
        self._listening_thread_ = Thread(target=self.listen)
        self._listening_thread_.start()

    def loadAnalyzer(self):
        from vosk import KaldiRecognizer
        from pymorphy2 import MorphAnalyzer

        self.rec = KaldiRecognizer(self.model(), self.rate)
        self.analyzer = MorphAnalyzer()
        self.ready = True

    def startListening(self):
        self._listening_ = True

    def stopListening(self):
        self._listening_ = False

    def listen(self):
        from PyAsoka.Asoka import Asoka
        from vosk import KaldiRecognizer

        while not self.ready:
            time.sleep(Asoka.defaultCycleDelay)

        while True:
            if self._listening_:
                self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                                                     rate=self.rate, input=True, frames_per_buffer=8000)
                self.rec = KaldiRecognizer(self.model(), self.rate)
                # print('listening')

                while True:
                    if not self._listening_:
                        # print('not listening')
                        self.stream.close()
                        break

                    data = self.stream.read(self.chunk, exception_on_overflow=True)

                    if self._listening_ and self.rec.AcceptWaveform(data) and len(data) > 0:
                        answer = json.loads(self.rec.Result())
                        if answer["text"]:
                            phrase = self.parsePhrase(answer['text'])
                            # print('Recognized: ', phrase.text())
                            self.recognized.emit(phrase)
                        self.rec = KaldiRecognizer(self.model(), self.rate)
            else:
                time.sleep(Asoka.defaultCycleDelay)

    def parsePhrase(self, text: str):
        phrase = Phrase()
        all_sym, words = self.splitText(text)
        for word in words:
            params = self.analyzer.parse(word)
            params = params[0]
            phrase += Word.create(word, params)
        return phrase

    def splitText(self, text: str):
        all_sym, words, word = [], [], ''
        for symbol in text:
            if symbol.isalpha():
                word += symbol

            else:
                if word != '':
                    all_sym.append(word)
                    words.append(word)
                    word = ''

                if symbol != ' ':
                    all_sym.append(symbol)

        if word != '':
            all_sym.append(word)
            words.append(word)

        return all_sym, words
