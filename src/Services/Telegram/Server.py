from PyAsoka.Asoka import Asoka

from pyrogram import Client, idle
from pyrogram.types import Message
from threading import Thread
from enum import Enum, auto

import asyncio


class Headers(Enum):
    Response = auto()
    ReceivedMessage = auto()

    getMe = auto()
    ReplyToMessage = auto()


def serverRun(api_id, api_hash, pipe):
    server = Server(api_id, api_hash, pipe)


class Server:
    def __init__(self, api_id, api_hash, pipe):
        self.id = api_id
        self.hash = api_hash
        self.pipe = pipe
        self.loop = asyncio.new_event_loop()
        self.client: 'Client' = None

        self.thread = Thread(target=self.loop.run_forever)
        self.thread.start()
        self.run()

    def send(self, header: Headers, data: dict):
        self.pipe.send({
            'header': header,
            'data': data
        })

    def response(self, rid, data: dict):
        self.pipe.send({
            'header': Headers.Response,
            'data': {'rid': rid, **data}
        })

    async def waitPipe(self):
        while True:
            if self.pipe.poll():
                message = self.pipe.recv()
                header, data = message['header'], message['data']

                if header == Headers.getMe:
                    self.response(data['rid'], {'user': await self.client.get_me()})

                elif header == Headers.ReplyToMessage:
                    chat_id, text = data['chat_id'], data['text']
                    await self.client.send_message(chat_id, text)

            else:
                await asyncio.sleep(Asoka.defaultCycleDelay)

    async def waitEvents(self):
        while True:
            await idle()

    def run(self):
        asyncio.set_event_loop(self.loop)

        self.client = Client('telegram', self.id, self.hash, workdir=Asoka.Project.Path.Home())

        @self.client.on_message()
        async def receiveMessage(client: Client, message: Message):
            if message is not None:
                self.send(Headers.ReceivedMessage, {'message': message})

        future = asyncio.run_coroutine_threadsafe(self.client.start(), self.loop)
        future.result()

        future = asyncio.run_coroutine_threadsafe(self.waitPipe(), self.loop)
        asyncio.run_coroutine_threadsafe(self.waitEvents(), self.loop)
        future.result()
