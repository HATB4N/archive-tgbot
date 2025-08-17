import asyncio
import contextlib
from downloader import Page2Pdf # not a p2p

class Interface:
    _pdf_maker: Page2Pdf.Dl
    _tasks_q: asyncio.Queue[tuple[str, int, int]]
    # target, flag, doc_id
    _results_q: asyncio.Queue[tuple[int, str, str]]
    # doc_id, path, title
    _workers: list[asyncio.Task]
    _started: bool
    _num_worker: int

    def __init__(self):
        self._pdf_maker = Page2Pdf.Dl()
        self._tasks_q = asyncio.Queue()
        self._results_q = asyncio.Queue()
        self._workers = []
        self._started = False
        self._num_worker = 3

    async def start(self):
        if self._started:
            return
        self._started = True
        print('downloader: start called')
        await self._pdf_maker.init()
        print('self.pdfmaker init done')

        for _ in range(self._num_worker):
            self._workers.append(asyncio.create_task(self._dl_worker()))
    
    async def stop(self):
        for t in self._workers:
            t.cancel()
        for t in self._workers:
            with contextlib.suppress(asyncio.CancelledError):
                await t
        self._workers.clear()
        self._started = False

    async def add_task(self, target: str, flag: int, doc_id: int):
         await self._tasks_q.put((target, flag, doc_id))

    async def _dl_worker(self): # what a dirty block...
        try:
            while(True):
                try:
                    target, flag, doc_id = await self._tasks_q.get()
                    match flag:
                        case 0: #flag = Default
                            print(f'dl start: {target}, {doc_id}')
                            ok, path, title, err = await self._pdf_maker.to_pdf(target, doc_id)
                            if ok:
                                # db state change to UPLOADING
                                # return to controller or alert to controller
                                await self._results_q.put((doc_id, path, title))
                                print(f'dl done: {target}, {doc_id}')
                            else:
                                # db state change to ERROR
                                print(f'dl fail: {err}')
                        case 1:
                            # idk
                            pass
                        case _:
                            # drop. (I've checked the flag already @ CmdTgbot before write)
                            pass
                finally:
                    self._tasks_q.task_done()
                    # asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def get_result(self) -> tuple[int, str]:
        return await self._results_q.get() # nowait test soon
    
    def result_done(self):
        self._results_q.task_done()