from pyrogram.types import Chat as TChat
from pyrogram.enums import ChatType


class Chat:
    Type = ChatType

    def __init__(self, chat: TChat):
        self._chat_ = chat

    @property
    def id(self):
        return self._chat_.id

    @property
    def type(self):
        return self._chat_.type

    @property
    def title(self):
        if self.type in (Chat.Type.CHANNEL, Chat.Type.GROUP, Chat.Type.SUPERGROUP):
            return self._chat_.title
        else:
            return None

    def isCreator(self):
        if self.type in (Chat.Type.CHANNEL, Chat.Type.GROUP, Chat.Type.SUPERGROUP):
            return self._chat_.is_creator
        else:
            return False


