from typing import Tuple
import asyncio
import Downloader
from tgbot import CmdTgbot
from tgbot import SendTgbot

class Con:
    _cbot: CmdTgbot.Tgbot
    _sbots: list[SendTgbot.Tgbot]

    def __init__(self, cbot, sbots):
        self._cbot = cbot
        self._sbots = sbots

    async def task(self):
        # read db & sbot.add_file & update db & cbot.alert_result
        pdf_maker = await Downloader.Web().init()

        while(True):
            print('start loop')
            url, flag, doc_id = await self._read()
            if flag == 'Default': # fix: flag to code
                r, p, e = await pdf_maker.to_pdf(url, doc_id)
                if r:
                    print('download done. send start.')
                    target_sbot = min(self._sbots, key=lambda b: b.len_q)
                    await self._cbot.alert_result(f'{url}: started to download\ndoc_id: {doc_id}')
                    await target_sbot.add_file(path=p, id=doc_id)
                else:
                    print('download fail.')
                    await self._cbot.alert_result(f'{url}: fail\n{e}') # fix
            else:
                print('flag: wip')
            print('done loop')
            await asyncio.sleep(5)

    async def _read(self) -> Tuple[str, str, int]:
        '''
        url: str, flag: str, id: int
        '''
        # flag to int (code)
        return 'https://google.com/', 'Default', 123