from pyrogram import Client
from matrixvcmusic import Matrixvcmusic

import config
from . import queues

client = Client(config.SESSION_NAME, config.API_ID, config.API_HASH)
Matrixvcmusic = Matrixvcmusic(client)


@matrixvcmusic.on_stream_end()
def on_stream_end(chat_id: int) -> None:
    queues.task_done(chat_id)

    if queues.is_empty(chat_id):
        matrixvcmusic.leave_group_call(chat_id)
    else:
        matrixvcmusic.change_stream(
            chat_id, queues.get(chat_id)["file"]
        )


run = matrixvcmusic.run
