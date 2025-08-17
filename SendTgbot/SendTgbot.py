import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder
from sqlalchemy import update, func, or_, select
from common.db import Session, Doc

class Tgbot:
    '''each obj's token must be unique'''
    _token: str
    _chat_id: str
    _api_svr: str
    _q: asyncio.Queue[tuple[int, str, str]]
    # doc_id, path, title
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

    def add_file(self, path: str, id: int, title: str): # add file & alert to queue
        print('sbot: file added')
        try:
            self._q.put_nowait((id, path, title))
            self.len_q = self._q.qsize()
        except:
            print('error')
            raise

    async def _queue_worker(self):
        try:
            while True:
                print('sbot: start loop')
                _doc_id, _path, _title = await self._q.get()
                self.len_q = self._q.qsize()
                try:
                    self.busy = 1
                    _msg_id = await self._send_file(path = _path, caption = _title)
                    ok = await self._write_index(doc_id=_doc_id, msg_id=_msg_id, title=_title)
                    if not ok:
                        print(f"sbot: id={_doc_id} wrong state")
                except Exception as e:
                    try:
                        await self._mark_fail(_doc_id, str(e))
                    except Exception as e2:
                        print("sbot: fail mark error:", e2)
                    raise
                finally:
                    self._q.task_done()
                    self.busy = 0
        except asyncio.CancelledError:
            # TODO
            pass

    async def _send_file(self, path: str, caption: str):
        print('sbot: send file')
        bot = self._app.bot
        with open(path, "rb") as f:
            msg = await bot.send_document(chat_id=self._chat_id, document=f, caption=caption)
        print('sbot: send file done')
        return msg.message_id

    async def _write_index(self, doc_id: int, msg_id: int, title: str | None) -> bool:
        t = (title or None)
        if t is not None:
            t = t.strip() or None
            if t is not None and len(t) > 200:
                t = t[:200]
        async with Session() as s:
            async with s.begin():
                res = await s.execute(
                    update(Doc)
                    .where(
                        Doc.doc_id == doc_id,
                        Doc.state.in_([10, 20, 30]),
                        or_(Doc.msg_id.is_(None), Doc.msg_id == msg_id),
                    )
                    .values(
                        msg_id=msg_id,
                        title=t if t is not None else Doc.title,
                        state=40,
                        updated_at=func.now(),
                    )
                )
        if res.rowcount == 1:
            return True
        async with Session() as s:
            got = await s.scalar(select(Doc.msg_id).where(Doc.doc_id == doc_id))
            return bool(got == msg_id)

    async def _mark_fail(self, doc_id: int, err: str) -> int:
        err500 = (err or "")[:500]
        async with Session() as s:
            async with s.begin():
                res = await s.execute(
                    update(Doc)
                    .where(Doc.doc_id == doc_id, Doc.state.in_([20, 30]))
                    .values(
                        state=100,
                        retry_count=(func.coalesce(Doc.retry_count, 0) + 1),
                        last_error=err500,
                        updated_at=func.now()
                    )
                )
            return res.rowcount  # 0이면 조건 불일치

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