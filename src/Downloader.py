from playwright.async_api import async_playwright
from typing import Tuple, Optional
# #import asyncio
import os

class Web:
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
    
    async def to_pdf(self, url, file_id) -> Tuple[bool, Optional[Exception]]:
        # match msg_id & file_id
        # not yet
        # I will refer to the archive box code later
        path = os.path.join(self._output_path, str(file_id) + '.pdf')
        try:
            page = await self._browser.new_page()
            await page.goto(url, wait_until="networkidle")
            await page.pdf(path=path, format="A4")
            await page.close()
            return True, None
        except Exception as e:
            return False, e

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None

# # test code
# async def main():
#     test = await Web().init()
#     r, e = await test.to_pdf(url = 'https://google.com', file_id = 123)
#     if not r:
#         print(e)
#     await test.close()

# if __name__ == '__main__':
#     asyncio.run(main())
    