from PyAsoka.Asoka import Asoka

from PyAsoka.src.Services.Telegram.Message import Message, TMessage

from threading import Thread

import asyncio


class Telegram:
    def __init__(self, api_id: int, api_hash: str):
        self.id = api_id
        self.hash = api_hash

        self.run()
        # self.thread = Thread(target=self.run)
        # self.thread.start()

    def sentToFavorite(self, content):
        pass

    def run(self):
        from pyrogram import Client
        self.client = Client('telegram', self.id, self.hash, workdir=Asoka.Project.Path.Home())

        @self.client.on_message()
        async def receiveMessage(client: Client, message: TMessage):
            message = Message(message)
            print(message.chat.title, message.sender.name, message.sender.surname, message.text)

        self.client.run()
