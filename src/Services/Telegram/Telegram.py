from PyAsoka.Asoka import Asoka

from PyAsoka.src.Services.Telegram.Message import Message, TMessage, User
from PyAsoka.src.Services.Telegram.Server import server, Headers

from pyrogram import Client, idle
from multiprocessing import Process, Pipe
from threading import Thread
from asyncio.windows_events import ProactorEventLoop

import asyncio


class Telegram:
    _current_ = None

    def __init__(self, api_id: int, api_hash: str):
        Telegram._current_ = self
        self._id_ = api_id
        self._hash_ = api_hash
        self._pipe_, child_pipe = Pipe()
        self._process_ = Process(target=server, args=(self._id_, self._hash_, child_pipe))
        self._process_.start()
        self._loop_ = asyncio.new_event_loop()
        self._client_: Client = None
        self._tasks_ = []

        self._loop_thread_ = Thread(target=self._loop_.run_forever)
        self._loop_thread_.start()
        self._thread_ = Thread(target=self.run)
        self._thread_.start()

    @property
    def id(self):
        return self._id_

    @property
    def hash(self):
        return self.hash

    @property
    def pipe(self):
        return self._pipe_

    @property
    def loop(self):
        return self._loop_

    @property
    def client(self):
        return self._client_

    def exec(self, task):
        return asyncio.run_coroutine_threadsafe(task, self.loop).result()

    def sendMessage(self, text):
        self._tasks_.append((self.client.send_message, {
            'chat_id': 'me',
            'text': text
        }))

    def add

    async def waitEvents(self):
        user = User(await self.client.get_me())
        print('Account:', user.username)
        while True:
            if self.pipe.poll():
                message = self.pipe.recv()
                header, data = message['header'], message['data']

                if header == Headers.ReceivedMessage:
                    message = Message(data)
                    print(message.chat.title, message.sender.username, message.text)
                    if message.text == 'привет':
                        print('replied')
                        await message.reply('Hello')
            else:
                await asyncio.sleep(Asoka.defaultCycleDelay)

    async def waitTasks(self):
        while True:
            if len(self._tasks_) > 0:
                func, kwargs = self._tasks_.pop()
                await func(**kwargs)
            await asyncio.sleep(Asoka.defaultCycleDelay)

    def run(self):
        from time import sleep
        asyncio.set_event_loop(self.loop)
        self._client_ = Client('telegram', self._id_, self._hash_, workdir=Asoka.Project.Path.Home())
        self.exec(self.client.start())

        future = asyncio.run_coroutine_threadsafe(self.waitEvents(), self.loop)
        asyncio.run_coroutine_threadsafe(self.waitTasks(), self.loop)

        future.result()

    @staticmethod
    def current() -> 'Telegram':
        return Telegram._current_


