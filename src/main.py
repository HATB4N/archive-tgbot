import asyncio
import Controller
from tgbot import CmdTgbot
from tgbot import SendTgbot

async def main():
    

    tokens = []
    # read tokens
    if not tokens:
        exit()

    sbots = [SendTgbot.Tgbot(token = token, chat_id = 'chat_id') for token in tokens] # add bot idx
    send_apps = [sbot.build() for sbot in sbots]

    cbot = CmdTgbot.Tgbot(token = 'token', chat_id = 'chat_id')
    cmd_app = cbot.build()

    ctr = Controller.Con(cbot = cbot, sbots = sbots)
    controller_task = asyncio.create_task(ctr.task())

    await asyncio.gather(
        cmd_app.run_polling(),
        *(send_app.run_polling() for send_app in send_apps),
        controller_task
    )

if __name__ == "__main__":
    asyncio.run(main())