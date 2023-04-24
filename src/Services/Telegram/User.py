from pyrogram.types import User as TUser
from pyrogram.enums import UserStatus


class User:
    Status = UserStatus

    def __init__(self, user: TUser):
        self._user_ = user

    @property
    def id(self):
        return self._user_.id

    @property
    def username(self):
        return self._user_.username

    @property
    def name(self):
        return self._user_.first_name

    @property
    def surname(self):
        return self._user_.last_name

    @property
    def status(self):
        return self._user_.status

    def isContact(self):
        return self._user_.is_contact

    def isBot(self):
        return self._user_.is_bot

    def toDict(self):
        return {

        }
