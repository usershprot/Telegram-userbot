import os
from telethon.tl.types import Message

async def log_cmd(client, message: Message, args):
    log_file = "forelka.log"
    if not os.path.exists(log_file):
        return await message.edit("❌ Log file not found")

    await message.edit("⌛️ Sending logs...")
    await client.send_file("me", log_file, caption="👻 Forelka Logs")
    await message.edit("✅ Logs sent to Saved Messages")


def register(app, commands, module_name):
    commands["log"] = {"func": log_cmd, "module": module_name}