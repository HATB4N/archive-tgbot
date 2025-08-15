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
    _app: None
    _flags = [] # wip

    def __init__(self, token, chat_id):
        '''
        don't make multiple CmdTgbot\n
        parse user's cmd & write it into db
        '''
        self._token = token
        self._chat_id = chat_id

    async def alert_result(self):
        pass

    async def _write(self, url: str, flag: str):
        pass

    async def _on_text(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        text = (u.effective_message.text or "").strip()
        # url + flag (ex: https://google.com --flag or http://naver.com --flag)
        m = re.match(r"^(https?://\S+)\s+--(\S+)$", text)
        if m:
            url = m.group(1)
            flag = m.group(2)
            if flag in self._flags:
                self._write(url = url, flag = flag)
            else:
                self._write(url = url, flag = 'default')

    async def _cmd_help(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        helptxt = ("flags\n"
                "--secretflag1\n"
                "--secretflag2\n"
                "--secretflag3\n"
                "--secretflag4\n")
        await c.bot.send_message(u.effective_chat.id, text=helptxt)
    
    def build(self):
        app = ApplicationBuilder().token(self._token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text))
        app.add_handler(CommandHandler("help", self._cmd_help))
        self._app = app
        return app

    def run(self):
        (self._app or self.build()).run_polling()