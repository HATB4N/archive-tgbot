import re
import asyncio
from enum import Enum, auto
from dataclasses import dataclass 
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    MessageHandler, 
    CommandHandler, 
    ContextTypes, 
    filters
)

from common.db import Session, Doc

# cmdbot은 dict[doc_id: file_t]을 통해 FSM에 기반하여 각 파일의 수명을 관리한다.
# 종료 state에(TERMINALS) 도달한 file_t은 dict에서 제거하는 방식으로 메모리를 관리한다. 
# 주기적으로 db에서 flag를 읽어와 file_t의 state를 관리한다.
# msg_id는 전송 이후 알 수 있으므로, doc_id에 매칭되는 dict로 구성한다. 
# doc_id는 cmdbot에서 업로드 요청을 db에 레코드 할 때 unique하게 발급받는다.
# WIP

class State(Enum):
    QUEUED = 0
    ENQUEUED = 5
    DOWNLOADING = 10
    DOWNLOADED = 20
    UPLOADING = 30
    UPLOADED = 40
    FAILED = 100
    
TERMINALS = {State.UPLOADED, State.FAILED}

@dataclass 
class file_t:
    msg_id: int = None
    target: str = None
    state: State = State.QUEUED
    flag: int = None
    

class Tgbot:
    _token: str
    _chat_id: str
    _worker_task: asyncio.Task | None
    _own_files: dict[int, file_t]
    _flags_match = {
        "Default": 0
    }

    def __init__(self, token, chat_id):
        '''
        don't make multiple CmdTgbot\n
        parse user's cmd & write it into db
        '''
        self._token = token
        self._chat_id = chat_id
        self._app = None
        self._bot = None
        self._worker_task = None
        self._own_files = dict[int, file_t] # trace file's life cycle

    async def _db_worker(self):
        try:
            while True:
                try:
                    pass
                finally:                    
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            # TODO
            pass

    async def _alert_result(self, res: str, bot=None):
        # call by _db_worker[uploaded or failed]
        pass

    async def _write(self, target: str, flag: int) -> int:
        async with Session() as s:
            async with s.begin():
                doc = Doc(target=target, flag=flag)
                s.add(doc)
                await s.flush()
                print(f'write new:\n  doc_id: {doc.doc_id}\n  state: {doc.state}')
            return doc.doc_id
        
    async def _on_text(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        print('etc get')
        text = (u.effective_message.text or "").strip()
        # url + flag (ex: https://google.com --flag or http://naver.com --flag)
        m = re.match(r"^(https?://\S+)(?:\s+--(\S+))?$", text)
        if m:
            target = m.group(1)
            flag = m.group(2)
            if flag not in list(self._flags_match.keys()):
                flag = 'Default'
            flag_num = self._flags_match[flag]
            print('etc start write')
            await self._write(target = target, flag = flag_num)
            print('etc write done')
            await c.bot.send_message(chat_id = self._chat_id, text=f'url: {target}\nflag: {flag}[{flag_num}]\nuploaded to queue')

    async def _cmd_help(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        print('send help')
        helptxt = ("flags\n"
                "--secretflag1\n"
                "--secretflag2\n"
                "--secretflag3\n"
                "--secretflag4\n")
        await c.bot.send_message(chat_id = self._chat_id, text=helptxt)
    
    def build(self):
        app = ApplicationBuilder().token(self._token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text))
        app.add_handler(CommandHandler("help", self._cmd_help))
        self._app = app
        self._bot = app.bot
        return app

    async def start_background(self):
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._db_worker())

    async def stop_background(self):
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None