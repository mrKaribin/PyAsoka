from PyAsoka.src.Services.Telegram.Chat import Chat
from PyAsoka.src.Services.Telegram.User import User

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
    def sender(self) -> User:
        return User(self._message_.from_user)

    @property
    def chat(self) -> Chat:
        return Chat(self._message_.chat)

    async def reply(self, text: str):
        from PyAsoka.src.Services.Telegram.Telegram import Telegram
        await Telegram.current().client.send_message(self.sender.id, text)
        # await self._message_.reply(text, *args, **kwargs)
