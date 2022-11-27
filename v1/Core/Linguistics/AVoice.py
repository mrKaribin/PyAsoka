import time

import speechd


class AVoiceSet:
    def __init__(self, engine='rhvoice', language='ru', voice='female2'):
        self.engine = engine
        self.language = language
        self.voice = voice


class AVoicePhrase:
    def __init__(self, text, voice_set, mode=0, priority=1, wait=False, callback=None):
        self.text = text
        self.voice_set = voice_set
        self.mode = mode
        self.priority = priority
        self.wait = wait
        self.callback = callback


class AVoice:
    SPEACH_NORMAL = 0
    SPEACH_FAST = 1

    PRIORITY_NORMAL = 1
    PRIORITY_LOW = 2
    PRIORITY_HIGH = 3

    def __init__(self, dialog, voice_set=AVoiceSet(), default_speed=0):
        self.dialog = dialog
        self.default_voice_set = voice_set
        self.voice_set = voice_set
        self.default_speed = default_speed
        self.speed = default_speed
        self.saying = False
        self.phrases = []
        self.current_phrase = None
        self.last_phrase = ''

        self.client = speechd.SSIPClient('Asoka')
        self.client.set_punctuation(speechd.PunctuationMode.SOME)
        self.__update_voice_set__()

    def __update_voice_set__(self):
        self.client.set_output_module(self.voice_set.engine)
        self.client.set_language(self.voice_set.language)
        self.client.set_voice(self.voice_set.voice)
        self.client.set_volume(-50)

    def say(self, text, mode=SPEACH_NORMAL, priority=PRIORITY_NORMAL, wait=False, callback=None, voice_set=None):
        if voice_set is None:
            voice_set = self.default_voice_set

        self.phrases.append(AVoicePhrase(text, voice_set, mode, priority, wait, callback))
        if self.saying:
            if self.current_phrase.priority < priority:
                self.client.stop()
                self.phrases.append(self.current_phrase)
                self.__say__()
        else:
            self.__say__()

    def __say__(self):
        for priority in [AVoice.PRIORITY_HIGH, AVoice.PRIORITY_NORMAL, AVoice.PRIORITY_LOW]:
            for phrase in self.phrases:
                if phrase.priority == priority:
                    self.current_phrase = phrase
                    self.phrases.remove(phrase)
                    speed = self.default_speed

                    if phrase.voice_set.engine != self.voice_set.engine:
                        self.voice_set = phrase.voice_set
                        self.__update_voice_set__()

                    if phrase.mode == AVoice.SPEACH_NORMAL:
                        speed = self.default_speed

                    if speed != self.speed:
                        self.speed = speed
                        self.client.set_rate(self.speed)

                    self.client.speak(phrase.text, callback=self.__said__)
                    self.last_phrase = phrase.text
                    if phrase.wait:
                        self.saying = True
                        while self.saying:
                            time.sleep(0.1)
                    return

    def __said__(self, param):
        if param == 'begin':
            self.dialog.saying(True)
            self.dialog.new_phrase(0, self.current_phrase.text)
            self.saying = True
        if param == 'end':
            self.dialog.saying(False)
            self.saying = False
            if self.current_phrase.callback is not None:
                self.current_phrase.callback()
            self.current_phrase = None
            self.__say__()
