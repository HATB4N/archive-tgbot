import os
import mysql.connector
from typing import Tuple, Optional
from playwright.async_api import async_playwright
# #import asyncio

class Dl:
    '''
    url, id -> return
    '''
    def __init__(self):
        self._browser = None
        self._output_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../downloads')
        )

    async def init(self):
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch()
        return self
    
    async def to_pdf(self, url, doc_id) -> Tuple[bool, Optional[str], Optional[Exception]]:
        # match msg_id & doc_id
        # not yet
        # I will refer to the archive box code later
        path = os.path.join(self._output_path, str(doc_id) + '.pdf')
        try:
            page = await self._browser.new_page()
            await page.goto(url, wait_until="networkidle") # fix after
            await page.pdf(path=path, format="A4") # also fix after
            await page.close()
            return True, path, None
        except Exception as e:
            return False, None, e

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None