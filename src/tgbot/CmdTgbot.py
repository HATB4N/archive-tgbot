import re
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

    async def alert_result(self, u: Update, c: ContextTypes.DEFAULT_TYPE, req: int, code: int):
        # WIP
        res = f''
        await c.bot.send_message(chat_id = self._chat_id, text=res)

    async def _write(self, url: str, flag: str):
        pass

    async def _on_text(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        text = (u.effective_message.text or "").strip()
        # url + flag (ex: https://google.com --flag or http://naver.com --flag)
        m = re.match(r"^(https?://\S+)\s+--(\S+)$", text)
        if m:
            url = m.group(1)
            flag = m.group(2).lower()
            if flag in self._flags:
                await self._write(url = url, flag = flag)
            else:
                await self._write(url = url, flag = 'Default')
        
    async def _cmd_rm(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        if not c.args:
            await u.message.reply_text("format: /rm <target_id>")
            return
        if c.args[0]:
            # TODO: validate target_id & search & rm it
            await u.message.reply_text("WIP")

    async def _cmd_help(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        helptxt = ("flags\n"
                "--secretflag1\n"
                "--secretflag2\n"
                "--secretflag3\n"
                "--secretflag4\n")
        await c.bot.send_message(chat_id = self._chat_id, text=helptxt)
    
    def build(self):
        app = ApplicationBuilder().token(self._token).base_url(self._api_svr).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text))
        app.add_handler(CommandHandler("rm", self._cmd_rm))
        app.add_handler(CommandHandler("help", self._cmd_help))
        return app