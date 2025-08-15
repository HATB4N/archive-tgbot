from telegram import Bot
from telegram.ext import ApplicationBuilder

class Tgbot:
    '''each obj's token must be unique'''
    _token: str
    _chat_id: str

    def __init__(self, token, chat_id):
        self._token = token
        self._chat_id = chat_id
    
    async def add_file(self, path: str): # add file & alert to queue
        pass

    async def _queue(slef):
        pass

    async def _send_file(self, path: str, caption: str):
        bot = Bot(self._token)
        with path.open("rb") as f:
            msg = await bot.send_document(self._chat_id, document=f, caption=caption)
        return msg.message_id

    async def _write_index(self):
        pass

    def run(self):
        app = ApplicationBuilder().token(self._token).build()
        app.run_polling()