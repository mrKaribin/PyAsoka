from PyAsoka.src.Network.Socket.Server import ServerSocket
from PyAsoka.Asoka import Asoka

from pyrogram import Client
from pyrogram.types import Message


class Headers:
    ReceivedMessage = 'receivedMessage'


def server(api_id, api_hash, pipe):
    telegram = Client('telegram_listener', api_id, api_hash, workdir=Asoka.Project.Path.Home())

    @telegram.on_message()
    async def receiveMessage(client: Client, message: Message):
        if message is not None:
            pipe.send({
                'header': Headers.ReceivedMessage,
                'data': message
            })

    telegram.run()
