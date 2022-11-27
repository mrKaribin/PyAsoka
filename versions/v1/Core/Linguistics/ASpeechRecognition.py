import struct

from PyAsoka.Core.Linguistics.APhrase import APhrase
from PyAsoka.Core.Linguistics.AWord import AWord
from vosk import Model, KaldiRecognizer, SetLogLevel
import PyAsoka.asoka as a
import os, pyaudio, pymorphy2, json

from PyAsoka.Instruments.Stopwatch import Stopwatch


class ASpeechRecModel:
    def __init__(self, path, lang: a.language):
        self.language = lang
        self._model_ = Model(path)

    def __call__(self, *args, **kwargs):
        return self._model_


class ASpeechRecognition:
    def __init__(self, model: ASpeechRecModel = None):
        if model is None:
            path = os.path.split(os.path.abspath(__file__))[0] + '/vosk-model-small-ru-0.22'
            model = ASpeechRecModel(path, a.language.russian)
        self.chunk = 8000
        self.rate = 16000
        self.model = model
        self.rec = KaldiRecognizer(self.model(), self.rate)
        self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                                             rate=self.rate, input=True, frames_per_buffer=8000)
        self.analyzer = pymorphy2.MorphAnalyzer()

    def listen(self):
        while True:
            timer = Stopwatch().start()
            data = self.stream.read(self.chunk, exception_on_overflow=True)
            # data_int = struct.unpack(str(self.chunk) + 'h', data)
            # print(data_int)

            if self.rec.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.rec.Result())
                if answer["text"]:
                    # print(f'Listened with {timer.finish()}s')
                    text = answer['text'].split(' ')
                    _phrase = APhrase([])
                    timer.start()
                    # print('Parsing... ', end='')
                    for word in text:
                        params = self.analyzer.parse(word)
                        params = params[0]
                        _phrase += AWord.create(word, params)
                    # print(f'ok with {timer.finish()}s')
                    return _phrase
            else:
                timer.finish()
