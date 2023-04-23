from pyrogram.types import Message as TMessage


class Message:
    def __init__(self, message: TMessage):
        self._message_ = message

    @property
    def id(self):
        return self._message_.id

    @property
    def text(self):
        return self._message_.text

    @property
    def sender(self):
        from PyAsoka.src.Services.Telegram.User import User
        return User(self._message_.from_user)

    @property
    def chat(self):
        from PyAsoka.src.Services.Telegram.Chat import Chat
        return Chat(self._message_.chat)
