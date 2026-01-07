import json
import os
from telethon.tl.types import Message

async def prefix_cmd(client, message: Message, args):
    user_id = message.from_id.user_id if hasattr(message.from_id, 'user_id') else message.from_id
    path = f"config-{user_id}.json"
    cfg = {"prefix": "."}
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                cfg = json.load(f)
        except:
            pass

    if not args:
        current = cfg.get("prefix", ".")
        return await message.edit(
            f"👻 Settings\nCurrent prefix: {current}"
        )

    new_prefix = args[0][:3]
    cfg["prefix"] = new_prefix
    with open(path, "w") as f:
        json.dump(cfg, f, indent=4)

    client.prefix = new_prefix
    await message.edit(
        f"👻 Settings\n✅ Prefix set to: {new_prefix}"
    )


def register(app, commands, module_name):
    commands["prefix"] = {"func": prefix_cmd, "module": module_name}
    commands["setprefix"] = {"func": prefix_cmd, "module": module_name}