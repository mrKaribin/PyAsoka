from PyAsoka.src.Linguistics.Phrase import Phrase
from PyAsoka.Asoka import Asoka

import time


class CommunicationAction:
    def __init__(self, model, callback):
        self.model = model,
        self.callback = callback


class CommunicationModel:
    def __init__(self):
        self.actions = []

    def addAction(self, model, callback):
        action = CommunicationAction(model, callback)
        self.actions.append(action)

    def exec(self, phrase):
        for action in self.actions:
            if action.model == phrase:
                action.callback()

    def run(self, engine):
        from PyAsoka.src.Linguistics import APhraseModelParser as Model

        name = engine.user.name.lower()
        print(name)
        hello_model = Model.parse(f'[N {name} [C окей привет здравствуй здорово [N ты [C тут здесь]] [N добрый [C день вечер утро]]]]')
        bye_model = Model.parse(f'[C пока забудь [L до скорого]]')
        engine.listening_start()
        while engine.active:
            phrase = engine.recognition.listen()
            text = phrase.text()
            if text == engine.phrases.last().text:
                continue

            if not engine.isListening and hello_model == phrase:
                engine.say('Привет, чем займемся?')
                engine.listening_start()
                continue

            if engine.isListening:
                engine.phrases.append(Phrase(text))

                if bye_model == phrase:
                    engine.say('Если понадоблюсь, только позовите')
                    engine.listening_stop()

                self.exec(phrase)
            time.sleep(Asoka.defaultCycleDelay)
