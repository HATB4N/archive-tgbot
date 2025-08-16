import asyncio
import mysql.connector
from typing import Tuple

from downloader import Page2Pdf # not a p2p 
import SendTgbot

class Con:
    _sbots: list[SendTgbot.Tgbot]

    def __init__(self, sbots):
        self._sbots = sbots
        self._assign_lock = asyncio.Lock()

    async def task(self):
        # read db & sbot.add_file & update db
        pdf_maker = await Page2Pdf.Dl().init()
        while(True):
            print('start loop')
            url, flag, doc_id = await self._read()
            if flag == 0:
                r, p, e = await pdf_maker.to_pdf(url, doc_id)
                if r:
                    print('download done. send start.')
                    async with self._assign_lock:
                        target_sbot = min(self._sbots, key=lambda b: (b.len_q + b.busy)) # watch
                        # fix to min(double(total file size))
                        target_sbot.add_file(path=p, id=doc_id)
                else:
                    print('download fail.')
            else:
                print('flag: wip')
            print('done loop')
            await asyncio.sleep(0)

    async def _read(self) -> Tuple[str, int, int]:
        '''
        url: str, flag: str, id: int
        '''
        # flag to int (code)
        return 'https://google.com', 0, 123