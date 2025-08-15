import re
from typing import Optional
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    MessageHandler, 
    CommandHandler, 
    ContextTypes, 
    filters
)

class Tgbot:
    _token: str
    _chat_id: str
    _api_svr: str
    _flags = [] # wip

    def __init__(self, token, chat_id, api_svr = 'https://api.telegram.org/'):
        '''
        don't make multiple CmdTgbot\n
        parse user's cmd & write it into db
        '''
        self._token = token
        self._chat_id = chat_id
        self._api_svr = api_svr
        self._app = None
        self._bot = None

    async def alert_result(self, res: str, bot=None):
        b = bot or getattr(self, "_bot", None)
        if b is None:
            raise RuntimeError("cbot: bot is None")
        await b.send_message(chat_id=self._chat_id, text=res)

    async def _write(self, url: str, flag: str):
        # TODO write to db
        # Default: int(0)
        pass

    async def _on_text(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        print('etc help')
        text = (u.effective_message.text or "").strip()
        # url + flag (ex: https://google.com --flag or http://naver.com --flag)
        m = re.match(r"^(https?://\S+)\s+--(\S+)$", text)
        if m:
            url = m.group(1)
            flag = m.group(2).lower()
            if flag not in self._flags:
                flag = 'Default'
            await self._write(url = url, flag = flag)
            await c.bot.send_message(chat_id = self._chat_id, text=f'url: {url}\nflag: {flag}\nhas uploaded to queue')
        
    async def _cmd_rm(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        if not c.args:
            await c.bot.send_message(chat_id = self._chat_id, text='format: /rm <target_id>')
            return
        if c.args[0]:
            # TODO: validate target_id & search & rm it
            await c.bot.send_message(chat_id = self._chat_id, text='WIP')

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
        app.add_handler(CommandHandler("rm", self._cmd_rm))
        app.add_handler(CommandHandler("help", self._cmd_help))
        self._app = app
        self._bot = app.bot
        return app