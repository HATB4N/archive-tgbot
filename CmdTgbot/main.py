import os
import signal
import asyncio
import contextlib

import CmdTgbot

async def main():
    env = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../env')
        )

    with open(os.path.join(env, 'cbotenv.txt'), 'r', encoding='utf-8') as f:
        envs = [ln.strip() for ln in f.read().splitlines() if ln.strip()]

    if len(envs) != 2:
        print("less token")
        exit()

    chat_id = envs[0]
    token = envs[1]
    
    bot = CmdTgbot.Tgbot(token = token, chat_id = chat_id)
    app = bot.build()

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    await asyncio.gather(app.initialize())
    await asyncio.gather(app.start())
    await asyncio.gather(
    app.updater.start_polling(allowed_updates=["message", "channel_post", "edited_message"]))

    await asyncio.gather(bot.start_background())

    try:
        await stop_event.wait()
    finally:
        await asyncio.gather(app.stop_background())
        await asyncio.gather(app.updater.stop()) # watch
        await asyncio.gather(app.stop())
        await asyncio.gather(app.shutdown())

if __name__ == '__main__':
    asyncio.run(main())