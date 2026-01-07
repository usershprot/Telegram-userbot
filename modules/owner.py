import json
import os
from telethon.tl.types import Message

async def addowner_cmd(client, message: Message, args):
    if not args and not message.reply_to_msg_id:
        return await message.edit(
            "❗️ Usage:\n"
            ".addowner [user_id] - добавить по ID\n"
            ".addowner (ответ на сообщение) - добавить пользователя"
        )

    if message.reply_to_msg_id:
        reply = await client.get_messages(message.chat_id, ids=message.reply_to_msg_id)
        user_id = reply.from_id.user_id if hasattr(reply.from_id, 'user_id') else reply.from_id
        user_name = getattr(reply.sender, 'first_name', f"User {user_id}")
    else:
        try:
            user_id = int(args[0])
            user_name = f"User {user_id}"
        except:
            return await message.edit("❌ Неверный ID")

    config_path = f"config-{client.me.id}.json"
    config = {"prefix": "."}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            pass

    owners = config.get("owners", [])
    if user_id in owners:
        return await message.edit(f"❗️ {user_name} уже является овнером")

    owners.append(user_id)
    config["owners"] = owners

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    await message.edit(f"✅ Овнер добавлен!\nUser: {user_name}\nID: {user_id}\nВсего овнеров: {len(owners)}")


async def delowner_cmd(client, message: Message, args):
    if not args and not message.reply_to_msg_id:
        return await message.edit(
            "❗️ Usage:\n"
            ".delowner [user_id] - удалить по ID\n"
            ".delowner (ответ на сообщение) - удалить пользователя"
        )

    if message.reply_to_msg_id:
        reply = await client.get_messages(message.chat_id, ids=message.reply_to_msg_id)
        user_id = reply.from_id.user_id if hasattr(reply.from_id, 'user_id') else reply.from_id
    else:
        try:
            user_id = int(args[0])
        except:
            return await message.edit("❌ Неверный ID")

    if user_id == client.me.id:
        return await message.edit("❌ Нельзя удалить владельца бота")

    config_path = f"config-{client.me.id}.json"
    config = {"prefix": "."}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            pass

    owners = config.get("owners", [])
    if user_id not in owners:
        return await message.edit("❌ Пользователь не является овнером")

    owners.remove(user_id)
    config["owners"] = owners

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    await message.edit(f"✅ Овнер удален!\nID: {user_id}\nОсталось овнеров: {len(owners)}")


async def owners_cmd(client, message: Message, args):
    config_path = f"config-{client.me.id}.json"
    config = {"prefix": "."}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            pass

    owners = config.get("owners", [])
    if client.me.id not in owners:
        owners.insert(0, client.me.id)

    if not owners:
        return await message.edit("❗️ Нет добавленных овнеров")

    text = "👻 Список овнеров\n\n"
    for i, owner_id in enumerate(owners, 1):
        if owner_id == client.me.id:
            text += f"✅ {owner_id} (Владелец бота)\n"
        else:
            text += f"➡️ {owner_id}\n"
    text += f"\nВсего: {len(owners)} овнеров"

    await message.edit(text)


def register(app, commands, module_name):
    commands["addowner"] = {"func": addowner_cmd, "module": module_name}
    commands["delowner"] = {"func": delowner_cmd, "module": module_name}
    commands["owners"] = {"func": owners_cmd, "module": module_name}