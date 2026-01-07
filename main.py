import asyncio
import os
import json
import sys
import subprocess
import time

from telethon import TelegramClient, events
import loader


class TerminalLogger:
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("forelka.log", "a", encoding="utf-8")
        self.ignore_list = [
            "PERSISTENT_TIMESTAMP_OUTDATED",
            "updates.GetChannelDifference",
            "RPC_CALL_FAIL",
            "Retrying \"updates.GetChannelDifference\""
        ]

    def write(self, m):
        if not m.strip():
            return
        if any(x in m for x in self.ignore_list):
            return
        self.terminal.write(m)
        self.log.write(m)
        self.log.flush()

    def flush(self):
        pass


sys.stdout = sys.stderr = TerminalLogger()


APP_CONFIG_API_ID = 17349
APP_CONFIG_API_HASH = "344583e45741c457fe1862106095a5eb"


def is_owner(client_id, user_id):
    path = f"config-{client_id}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return user_id in json.load(f).get("owners", [])
        except:
            pass
    return False


def get_prefix(client_id):
    path = f"config-{client_id}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("prefix", ".")
        except:
            pass
    return "."


async def process_command(client, event, owner_only=False):
    if not event.text:
        return

    me = await client.get_me()
    prefix = get_prefix(me.id)

    if not event.text.startswith(prefix):
        return

    if owner_only and not is_owner(me.id, event.sender_id):
        return

    parts = event.text[len(prefix):].split(maxsplit=1)
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1].split() if len(parts) > 1 else []

    if cmd in client.commands:
        try:
            await client.commands[cmd]["func"](client, event, args)
        except Exception as e:
            print(f"Ошибка в команде {cmd}: {e}")


async def main():
    sess = next((f for f in os.listdir() if f.startswith("forelka-") and f.endswith(".session")), None)

    if sess:
        client = TelegramClient(sess[:-8], APP_CONFIG_API_ID, APP_CONFIG_API_HASH)
    else:
        temp = TelegramClient("temp", APP_CONFIG_API_ID, APP_CONFIG_API_HASH)
        print("📱 Введите номер телефона в формате +7ХXXXXXXXXX:")
        await temp.start(phone=lambda: input("Номер телефона: "))
        me = await temp.get_me()
        await temp.disconnect()
        os.rename("temp.session", f"forelka-{me.id}.session")
        client = TelegramClient(f"forelka-{me.id}", APP_CONFIG_API_ID, APP_CONFIG_API_HASH)

    client.commands = {}
    client.loaded_modules = set()

    await client.start()
    me = await client.get_me()
    client.start_time = time.time()

    @client.on(events.NewMessage(outgoing=True))
    async def outgoing(event):
        await process_command(client, event)

    @client.on(events.NewMessage(incoming=True))
    async def incoming(event):
        await process_command(client, event, owner_only=True)

    @client.on(events.MessageEdited(outgoing=True))
    async def edited(event):
        await process_command(client, event)

    try:
        loader.load_all(client)
        print("✅ Модули загружены успешно")
    except Exception as e:
        print(f"❌ Ошибка загрузки модулей: {e}")

    git = "unknown"
    try:
        git = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except:
        pass

    print(f"""
  __               _ _         
 / _|             | | |        
| |_ ___  _ __ ___| | | ____ _ 
|  _/ _ \\| '__/ _ \\ | |/ / _` |
| || (_) | | |  __/ |   < (_| |
|_| \\___/|_|  \\___|_|_|\\_\\__,_|

Forelka Started | Git: #{git}
User: @{me.username if me.username else me.id}
ID: {me.id}
""")

    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nForelka остановлен")
    except Exception as e:
        print(f"Критическая ошибка: {e}")