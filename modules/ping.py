import time
from telethon.tl.types import Message

async def ping_cmd(client, message: Message, args):
    start = time.perf_counter()
    await message.edit("⌛️ Pinging...")

    ms = (time.perf_counter() - start) * 1000
    res = (
        "👻 Pong\n"
        f"✅ Latency: {ms:.2f} ms"
    )
    await message.edit(res)


def register(app, commands, module_name):
    commands["ping"] = {"func": ping_cmd, "module": module_name}