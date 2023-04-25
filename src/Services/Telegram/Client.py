from PyAsoka.src.Services.Telegram.Message import Message
from PyAsoka.src.Services.Telegram.User import User
from PyAsoka.src.Services.Telegram.Chat import Chat
from PyAsoka.src.Services.Telegram.Server import serverRun, Headers
from PyAsoka.src.Linguistics.PhraseModel import PhraseModel
from PyAsoka.src.Core.Object import Object, Signal
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.Asoka import Asoka

from multiprocessing import Process, Pipe
from threading import Thread
from time import sleep

import asyncio
import random


class Client(Object):
    _current_ = None

    ChatType = Chat.Type

    messageReceived = Signal(Message, dict)

    class Request:
        def __init__(self, header, handler=None):
            self._header_ = header
            self._handler_ = handler
            self._response_ = None
            self._status_ = False

        @property
        def done(self):
            return self._status_

        @property
        def response(self):
            if self._status_:
                return self._response_
            else:
                raise Exception('Ответ на запрос еще не готов')

        def setResponse(self, reply):
            if self._handler_ is not None:
                self._response_ = self._handler_(reply)
            else:
                self._response_ = reply
            self._status_ = True

        def waitForResponse(self):
            from time import sleep
            while self._status_ is False:
                sleep(Asoka.defaultCycleDelay)
            return self._response_

    class ReplyPattern:
        def __init__(self, model: PhraseModel, replies: list = None,
                     chat_id: int | None = None, chat_type: Chat.Type | None = None):
            if replies is None:
                replies = []

            self._chat_id_ = chat_id
            self._chat_type_ = chat_type
            self._model_ = model
            self._replies_ = replies

        def __eq__(self, message: Message):
            id_cond = self.chatId is None or self.chatId == message.chat.id
            type_cond = self.chatType is None or self.chatType == message.chat.type
            text_cond = self._model_ == message.phrase
            return id_cond and type_cond and text_cond

        @property
        def chatId(self):
            return self._chat_id_

        @property
        def chatType(self):
            return self._chat_type_

        @property
        def reply(self):
            return self._replies_[random.randint(0, len(self._replies_) - 1)]

    def __init__(self, api_id: int, api_hash: str):
        super().__init__()
        Client._current_ = self
        self._id_ = api_id
        self._hash_ = api_hash
        self._pipe_, child_pipe = Pipe()
        self._auth_hash_: str = None
        self._auth_code_: str = None
        self._requests_ = {}
        self._reply_patterns_ = []

        self._process_ = Process(target=serverRun, args=(self._id_, self._hash_, child_pipe))
        self._thread_ = Thread(target=self.run)

    @property
    def id(self):
        return self._id_

    @property
    def hash(self):
        return self.hash

    @property
    def pipe(self):
        return self._pipe_

    def haveSession(self):
        from os.path import exists
        return exists(Asoka.Project.Path.Home() + '\\telegram.session')

    def __auth_run__(self, phone):
        from pyrogram import Client as TClient

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        client = TClient('telegram', self._id_, self._hash_)
        client.connect()
        code_info = client.send_code(phone)
        self._auth_hash_ = code_info.phone_code_hash

        while self._auth_code_ is None:
            sleep(Asoka.defaultCycleDelay)

        print('Phone:', phone)
        print('Code hash:', self._auth_hash_)
        print('Code:', self._auth_code_)
        result = client.sign_in(phone, self._auth_hash_, self._auth_code_)
        print(type(result))
        client.disconnect()

        client.start()
        client.stop()

    def sendAuthCode(self, phone: str):
        self._auth_thread_ = Thread(target=self.__auth_run__, args=(phone,))
        self._auth_thread_.start()
        while self._auth_hash_ is None:
            sleep(Asoka.defaultCycleDelay)
        return self._auth_hash_

    def authWithCode(self, code):
        self._auth_code_ = code
        self._auth_thread_.join()
        sleep(4)

    def start(self):
        self._thread_.start()
        self._process_.start()

    def send(self, header: Headers, data: dict):
        self.pipe.send({
            'header': header,
            'data': data
        })

    def request(self, header, data: dict, handler=None):
        request = Client.Request(header, handler)
        self._requests_[id(request)] = request
        self.pipe.send({
            'header': header,
            'data': {'rid': id(request), **data}
        })
        return request

    def user(self, sync=True):
        request = self.request(Headers.getMe, {}, lambda data: User(data['user']))
        if sync:
            return request.waitForResponse()
        else:
            return request

    def sendMessage(self, chat_id: int, text: str):
        self.send(Headers.ReplyToMessage, {'chat_id': chat_id, 'text': text})

    def addReplyPattern(self, pattern: PhraseModel | str, *args, **kwargs):
        if isinstance(pattern, str):
            pattern = PhraseModel.parse(pattern)
        self._reply_patterns_.append(Client.ReplyPattern(pattern, *args, **kwargs))

    def run(self):
        from time import sleep
        user: 'User' = None
        req = self.user(False)

        while True:
            if req is not None and req.done:
                user = req.response
                req = None
                print('User:', user.username)

            if self.pipe.poll():

                # try:
                message = self.pipe.recv()
                header, data = message['header'], message['data']

                if header == Headers.Response:
                    rid = data['rid']
                    if (request := self._requests_.pop(rid, None)) is not None:
                        request.setResponse(data)

                elif user is not None:
                    if header == Headers.ReceivedMessage:
                        message, reply = Message(data['message']), None
                        if message.chat.type == Chat.Type.PRIVATE:
                            print(f'{message.sender.name} {message.sender.surname}: {message.text}')
                        elif message.chat.type == Chat.Type.CHANNEL:
                            print(f'{message.chat.title}: {message.text}')
                        else:
                            print(f'({message.chat.title}) {message.sender.name} {message.sender.surname}: {message.text}')
                        if (message.sender is None or message.sender.id != user.id) and message.text is not None:
                            for pattern in self._reply_patterns_:
                                if pattern == message:
                                    reply = pattern.reply
                                    print('Replied:', reply)
                                    message.reply(reply)
                                    break
                        self.messageReceived.emit(message, {'reply': reply})

                # except Exception as e:
                #     Logs.warning(f'Telegram.run(): {e}')
            else:
                sleep(Asoka.defaultCycleDelay)

    @staticmethod
    def current() -> 'Client':
        return Client._current_


