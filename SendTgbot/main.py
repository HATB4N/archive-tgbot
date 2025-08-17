import os
import signal
import asyncio
import contextlib
import Controller
import SendTgbot
from common.db import init_models

async def main():
    env = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../env')
        )

    with open(os.path.join(env, 'sbotenv.txt'), 'r', encoding='utf-8') as f:
        envs = [ln.strip() for ln in f.read().splitlines() if ln.strip()]

    if len(envs)< 2:
        print("less env args")
        exit()
    
    sbot_chat_id = envs.pop(0)

    sbots = [SendTgbot.Tgbot(token=str(t), chat_id=int(sbot_chat_id)) for t in envs]
    apps = [b.build() for b in sbots]

    async def bootstrap_db(max_try=20, delay=1.5):
        for i in range(max_try):
            try:
                await init_models()
                print("[db] models ready")
                return
            except Exception as e:
                print(f"[db] not ready ({i+1}/{max_try}): {e}")
                await asyncio.sleep(delay)
        raise RuntimeError("DB init failed")
    
    await bootstrap_db()

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass
    

    ctr = Controller.Con(sbots = sbots)
    controller_task = asyncio.create_task(ctr.task())

    await asyncio.gather(*(app.initialize() for app in apps))
    await asyncio.gather(*(app.start() for app in apps))
    await asyncio.gather(
    *(app.updater.start_polling(allowed_updates=["message", "channel_post", "edited_message"]) for app in apps)
    )

    await asyncio.gather(*(b.start_background() for b in sbots))

    try:
        await stop_event.wait()
    finally:
        await asyncio.gather(*(b.stop_background() for b in sbots))
        await asyncio.gather(*(app.updater.stop() for app in reversed(apps))) # watch
        await asyncio.gather(*(app.stop() for app in reversed(apps)))
        await asyncio.gather(*(app.shutdown() for app in reversed(apps)))
        controller_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await controller_task

if __name__ == "__main__":
    asyncio.run(main())