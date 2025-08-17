import os
from typing import Tuple, Optional
from playwright.async_api import async_playwright, TimeoutError
from playwright_stealth import Stealth

class Dl:
    '''
    url, doc_id -> res: bool, path: str, e: exception
    '''
    def __init__(self):
        self._browser = None
        self._output_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../downloads')
        )

    async def init(self):
        print('page2pdf: start init()')
        if not self._browser:
            self._playwright = Stealth().use_async(async_playwright())
            self._p = await self._playwright.__aenter__() 
            self._browser = await self._p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
        return self
    
    async def to_pdf(self, url, doc_id) -> Tuple[bool, Optional[str], Optional[str], Optional[Exception]]:
        path = os.path.join(self._output_path, str(doc_id) + '.pdf')
        try:
            ctx = (self._browser.contexts[0] if self._browser.contexts else await self._browser.new_context())
            resp = await ctx.request.get(url, timeout=30_000, fail_on_status_code=False)
            ct = (resp.headers or {}).get("content-type", "").lower()
            if "application/pdf" in ct:
                cd = (resp.headers or {}).get("content-disposition", "")
                filename = None
                if "filename=" in cd.lower():
                    filename = cd.split("filename=")[-1].strip('" ')
                if not filename:
                    from urllib.parse import urlparse
                    filename = os.path.basename(urlparse(url).path) or "PDF Document"
                title = filename
                body = await resp.body()
                with open(path, "wb") as f:
                    f.write(body)
                return True, path, title, None


            page = await self._browser.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            except TimeoutError:
                pass
            title = await page.title()
            try:
                await page.evaluate("""
                    (async () => {
                        const step = Math.floor(window.innerHeight * 0.8);
                        const delay = 100;
                        function sleep(ms){ return new Promise(r=>setTimeout(r, ms)); }
                        const se = document.scrollingElement || document.documentElement;
                        let prevBottom = -1, sameCount = 0;
                        while (true){
                            const atBottom = se.scrollHeight - (se.scrollTop + window.innerHeight) <= 2;
                            if (atBottom) {
                                const cur = se.scrollHeight;
                                sameCount = (cur === prevBottom) ? sameCount + 1 : 0;
                                prevBottom = cur;
                                if (sameCount >= 3) break;
                            } else {
                                se.scrollBy(0, step);
                            }
                            await sleep(delay);
                        }
                    })();
                """)
            except:
                pass
            
            await page.wait_for_timeout(800)
            try:
                await page.wait_for_load_state("networkidle", timeout=20000)
            except TimeoutError:
                pass

            await page.pdf(
                path=path,
                print_background=True,
                # need test
                prefer_css_page_size=False,
                width="1920px",
                height="2700px"
                )
            await page.close()
            return True, path, title, None # ok, path, title, err
        except Exception as e:
            return False, None, None, e # ok, path, title, err

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._p:
            await self._p.stop()
            self._p = None