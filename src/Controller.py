import asyncio
import Downloader

class Con:
    _cbot: object
    _sbots: object

    def __init__(self, cbot, sbots):
        self._cbot = cbot
        self._sbots = sbots
        #ex: self._sbots[0].add_file('path/to/file')

    async def task(self):
        # read db & sbot.add_file & update db & cbot.alert_result
        pdf_maker = await Downloader.Web().init()

        while(True):
            self._read()
            asyncio.sleep(1)

    async def _read(self):
        pass