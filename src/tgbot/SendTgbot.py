from telegram import Bot
from telegram.ext import ApplicationBuilder

class Tgbot:
    '''each obj's token must be unique'''
    _token: str
    _chat_id: str
    _api_svr: str

    def __init__(self, token, chat_id, api_svr = 'https://api.telegram.org/'):
        self._token = token
        self._chat_id = chat_id
        self._api_svr = api_svr
    
    async def add_file(self, path: str): # add file & alert to queue
        pass

    async def _queue(slef):
        pass

    async def _send_file(self, path: str, caption: str):
        bot = Bot(self._token)
        with path.open("rb") as f:
            msg = await bot.send_document(chat_id=self._chat_id, document=f, caption=caption)
        return msg.message_id

    async def _write_index(self):
        pass

    def build(self):
        app = ApplicationBuilder().token(self._token).base_url(self._api_svr).build()
        return app