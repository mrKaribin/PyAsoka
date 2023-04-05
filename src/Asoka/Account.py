

class Account:
    def __init__(self):
        self._login_ = ''
        self._authorized_ = False

    @property
    def login(self):
        return self._login_

    @property
    def authorized(self):
        return self._authorized_

    def setLogin(self, login):
        self._login_ = login
