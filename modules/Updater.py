import os
import sys
import time
import asyncio
import subprocess

async def update_cmd(event, client, args):
    """Обновление бота через git pull"""
    try:
        await event.edit("⌛️ <b>Updating...</b>", parse_mode="html")
        res = subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT).decode()
        if "Already up to date" in res:
            return await event.edit("❗️ <b>Already up to date</b>", parse_mode="html")

        # Сохраняем инфу для уведомления после рестарта
        os.environ["RESTART_INFO"] = f"{time.time()}|{event.chat_id}|{event.id}"
        os.execv(sys.executable, [sys.executable, "main.py"])

    except Exception as e:
        await event.edit(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode="html")


async def restart_cmd(event, client, args):
    """Ручной рестарт бота"""
    os.environ["RESTART_INFO"] = f"{time.time()}|{event.chat_id}|{event.id}"
    await event.edit("⌛️ <b>Restarting...</b>", parse_mode="html")
    os.execv(sys.executable, [sys.executable, "main.py"])


def register(client, commands):
    commands["update"] = update_cmd
    commands["restart"] = restart_cmd

    # Проверка, был ли рестарт и нужно ли уведомить
    restart_data = os.environ.get("RESTART_INFO")
    if restart_data:
        try:
            start_time, chat_id, msg_id = restart_data.split("|")
            diff = time.time() - float(start_time)

            async def notify_start():
                await asyncio.sleep(1.5)
                await client.edit_message(
                    int(chat_id),
                    int(msg_id),
                    f"👻 <b>Forelka Started</b>\n"
                    f"✅ <b>Restart time:</b> <code>{diff:.2f}s</code>",
                    parse_mode="html"
                )

            asyncio.get_event_loop().create_task(notify_start())
            os.environ.pop("RESTART_INFO", None)
        except:
            pass