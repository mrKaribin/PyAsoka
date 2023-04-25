from PyAsoka.src.Services.Telegram.Chat import Chat
from PyAsoka.src.Services.Telegram.User import User

from pyrogram.types import Message as TMessage


class Message:
    def __init__(self, message: TMessage):
        self._message_ = message
        self._phrase_ = None

    @property
    def id(self):
        return self._message_.id

    @property
    def text(self):
        return self._message_.text

    @property
    def phrase(self):
        if self.text is None:
            return None
        if self._phrase_ is None:
            from PyAsoka.src.Core.Core import core
            self._phrase_ = core().communication.recognition.parsePhrase(self.text)
        return self._phrase_

    @property
    def sender(self) -> User | Chat | None:
        if (user := self._message_.from_user) is not None:
            return User(user)
        else:
            return None

    @property
    def chat(self) -> Chat:
        return Chat(self._message_.chat)

    def reply(self, text: str):
        from PyAsoka.src.Services.Telegram.Client import Client
        return Client.current().sendMessage(self.sender.id, text)
