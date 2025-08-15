import os
import signal
import asyncio
import subprocess
import Controller
from tgbot import CmdTgbot
from tgbot import SendTgbot

def wtf():
    img = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../etc/img.png')
    )
    subprocess.run(["chafa", '--size=40', img])

async def main():
    env = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../env')
        )

    with open(os.path.join(env, 'tokens.txt'), 'r', encoding='utf-8') as f:
        tokens = [ln.strip() for ln in f.read().splitlines() if ln.strip()]

    if len(tokens)< 2:
        print("less token")
        exit()
    
    with open(os.path.join(env, 'chat_ids.txt'), 'r', encoding='utf-8') as f:
        chat_ids = [ln.strip() for ln in f.read().splitlines() if ln.strip()]

    if len(chat_ids)< 2:
        print("less chat_id")
        exit()

    cbot_chat_id = chat_ids[0]
    sbot_chat_id = chat_ids[1]

    cbot_token = tokens.pop(0).strip() # first line of token.txt => cbot_token 
    cbot = CmdTgbot.Tgbot(token = str(cbot_token), chat_id = int(cbot_chat_id))
    cmd_app = cbot.build()

    sbots = [SendTgbot.Tgbot(token=str(t), chat_id=int(sbot_chat_id)) for t in tokens]
    send_apps = [b.build() for b in sbots]

    apps = [cmd_app, *send_apps]
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass
    

    ctr = Controller.Con(cbot = cbot, sbots = sbots)
    controller_task = asyncio.create_task(ctr.task())

    await asyncio.gather(*(app.initialize() for app in apps))
    await asyncio.gather(*(app.start() for app in apps))

    await asyncio.gather(
    *(app.updater.start_polling(allowed_updates=["message", "channel_post", "edited_message"]) for app in apps)
    )

    try:
        await stop_event.wait()
    finally:
        await asyncio.gather(*(app.stop() for app in reversed(apps)))
        await asyncio.gather(*(app.shutdown() for app in reversed(apps)))
        controller_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await controller_task

if __name__ == "__main__":
    wtf()
    import contextlib
    asyncio.run(main())