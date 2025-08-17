import asyncio
from typing import Tuple, Optional

from downloader import Downloader
import SendTgbot
from sqlalchemy import select, update, func
from common.db import Session, Doc

class Con:
    _sbots: list[SendTgbot.Tgbot]
    _dl: Downloader.Interface

    def __init__(self, sbots):
        self._sbots = sbots
        self._assign_lock = asyncio.Lock()
        self._dl = Downloader.Interface()

    async def _produce_loop(self):
        while True:
            target, flag, doc_id = await self._read() # STATE = 5(ENQUEUED)
            await self._dl.add_task(target, flag, doc_id)
            await asyncio.sleep(1)

    async def _consume_loop(self):
        while True:
            _doc_id, _path, _title = await self._dl.get_result()  # 결과가 올 때만 대기
            # download completed files
            await self.update_state(doc_id = _doc_id, state = 10, exp_state=[5])
            try:
                async with self._assign_lock:
                    target_sbot = min(self._sbots, key=lambda b: (b._q.qsize() + b.busy, id(b)))
                    target_sbot.add_file(path = _path, id = _doc_id, title = _title)
            finally:
                self._dl.result_done()

    async def task(self):
        print('task start')
        await self._dl.start()
        print('dl start done')
        producer = asyncio.create_task(self._produce_loop())
        consumer = asyncio.create_task(self._consume_loop())
        try:
            await asyncio.gather(producer, consumer)
        except asyncio.CancelledError:
            pass
        finally:
            await self._dl.stop()

    async def _read(self) -> Tuple[Optional[str], Optional[int], Optional[int]]:
        """
        대기 상태(state=0) 중 가장 이른 doc 하나를 가져온다. (FIFO)
        (target, flag, doc_id)
        """
        print('read loop start')
        while(True):
            async with Session() as s:
                async with s.begin():
                    q = (
                        select(Doc)
                        .where(Doc.state == 0)
                        .order_by(Doc.doc_id.asc())
                        .limit(1)
                        .with_for_update(skip_locked=True)
                    )
                    doc = (await s.scalars(q)).first()
                    if doc:
                        doc.state = 5 # ENQUEUED
                        doc.updated_at = func.now()
                        print('read return valid values')
                        return doc.target, doc.flag, doc.doc_id
                await asyncio.sleep(3)

    async def update_state(self, doc_id: int, state: int, exp_state: list[int]) -> int:
        """
        if doc.state = exp_state : doc.state == state
        """
        async with Session() as s:
            async with s.begin():
                res = await s.execute(
                    update(Doc)
                    .where(Doc.doc_id == doc_id, Doc.state.in_(exp_state))
                    .values(
                        state=state,
                        updated_at=func.now()
                    )
                )
                return res.rowcount