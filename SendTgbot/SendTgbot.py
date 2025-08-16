import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder

class Tgbot:
    '''each obj's token must be unique'''
    _token: str
    _chat_id: str
    _api_svr: str
    _q: asyncio.Queue[tuple[int, str, str]]
    _worker_task: asyncio.Task | None
    len_q: int
    busy: bool

    def __init__(self, token, chat_id, api_svr = 'https://api.telegram.org/'):
        self._token = token
        self._chat_id = chat_id
        self._api_svr = api_svr
        self._q = asyncio.Queue()
        self._worker_task = None
        self.len_q = 0
        self.busy = 0

    async def _queue_worker(self):
        try:
            while True:
                print('sbot: start loop')
                _doc_id, _path, _caption = await self._q.get()
                self.len_q = self._q.qsize()
                try:
                    self.busy = 1
                    _msg_id = await self._send_file(path = _path, caption = _caption)
                    await self._write_index(doc_id = _doc_id, msg_id = _msg_id)
                finally:                    
                    self._q.task_done()
                    self.busy = 0
        except asyncio.CancelledError:
            # TODO
            pass

    def add_file(self, path: str, id: int, caption: str = ""): # add file & alert to queue
        print('sbot: file added')
        try:
            self._q.put_nowait((id, path, caption))
            self.len_q = self._q.qsize()
        except:
            print('error')
            raise

    async def _send_file(self, path: str, caption: str):
        print('sbot: send file')
        bot = self._app.bot
        with open(path, "rb") as f:
            msg = await bot.send_document(chat_id=self._chat_id, document=f, caption=caption)
        print('sbot: send file done')
        return msg.message_id

    async def _write_index(self, doc_id: int, msg_id: int):
        pass

    def build(self):
        app = ApplicationBuilder().token(self._token).build()
        self._app = app
        return app
    
    async def start_background(self):
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._queue_worker())

    async def stop_background(self):
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None