import asyncio
import mysql.connector
from typing import Tuple

from downloader import Downloader
import SendTgbot

class Con:
    _sbots: list[SendTgbot.Tgbot]
    _dl: Downloader.Interface

    def __init__(self, sbots):
        self._sbots = sbots
        self._assign_lock = asyncio.Lock()
        self._dl = Downloader.Interface()

    async def _produce_loop(self):
        while True:
            uri, flag, doc_id = await self._read()
            await self._dl.add_task(uri, flag, doc_id)
            await asyncio.sleep(1)

    async def _consume_loop(self):
        while True:
            doc_id, out_path = await self._dl.get_result()  # 결과가 올 때만 대기
            try:
                async with self._assign_lock:
                    target_sbot = min(self._sbots, key=lambda b: (b._q.qsize() + b.busy, id(b)))
                    target_sbot.add_file(path = out_path, id = doc_id)
            finally:
                self._dl.result_done()

    async def task(self):
        # read db & sbot.add_file & update db
        await self._dl.start()
        producer = asyncio.create_task(self._produce_loop())
        consumer = asyncio.create_task(self._consume_loop())
        try:
            await asyncio.gather(producer, consumer)
        except asyncio.CancelledError:
            pass
        finally:
            await self._dl.stop()

    async def _read(self) -> Tuple[str, int, int]:
        '''
        uri: str, flag: int, doc_id: int
        '''
        # test
        url_test = ''
        return url_test, 0, 123
    
    async def _add_msg_id(self, doc_id: int, msg_id: int):
        # write msg_id
        pass

    async def _change_flag(self, doc_id: int):
        pass