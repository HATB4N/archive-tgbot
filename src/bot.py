from telegram import Bot
from telegram.ext import ApplicationBuilder

class Tgbot:
    _token: str
    _chat_id: str

    def __init__(self, token, chat_id):
        self._token = token
        self._chat_id = chat_id
    
    async def add_file(self):
        pass

    async def _queue(slef):
        pass

    async def _send_file(self, path, caption: str):
        bot = Bot(self._token)
        with path.open("rb") as f:
            msg = await bot.send_document(self._chat_id, document=f, caption=caption)
        return msg.message_id

    async def _write_index(self):
        pass

    def run(self):
        app = ApplicationBuilder().token(self._token).build()
        app.run_polling(allowed_updates=[])

# # test codes
# bot = Tgbot('token', 'chat_id')
# bot._send_file('a', 'b')
# bot.run()
