from PyAsoka.src.Linguistics.Phrase import Phrase
from PyAsoka.src.Linguistics.Word import Word
from PyAsoka.Asoka import Asoka
from vosk import Model, KaldiRecognizer

import os
import pyaudio
import pymorphy2
import json


class SpeechRecModel:
    def __init__(self, path, lang: Asoka.Language):
        self.language = lang
        self._model_ = Model(path)

    def __call__(self, *args, **kwargs):
        return self._model_


class SpeechRecognition:
    class Models:
        PERFORMANCE = os.path.split(os.path.abspath(__file__))[0] + '/vosk-model-small-ru-0.22'
        QUALITY = os.path.split(os.path.abspath(__file__))[0] + '/vosk-model-ru-0.22'

    def __init__(self, model: SpeechRecModel = None):
        if model is None:
            path = self.Models.QUALITY
            model = SpeechRecModel(path, Asoka.Language.RUSSIAN)
        self.chunk = 8000
        self.rate = 16000
        self.model = model
        self.rec = KaldiRecognizer(self.model(), self.rate)
        self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                                             rate=self.rate, input=True, frames_per_buffer=8000)
        self.analyzer = pymorphy2.MorphAnalyzer()

    def listen(self):
        while True:
            data = self.stream.read(self.chunk, exception_on_overflow=True)

            if self.rec.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.rec.Result())
                if answer["text"]:
                    phrase = self.parsePhrase(answer['text'])
                    print(phrase)
                    return phrase

    def parsePhrase(self, text: str):
        phrase = Phrase()
        all_sym, words = self.splitText(text)
        # words = text.split(' ')
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
