import sys
import asyncio
import os
from telethon.tl.types import Message

async def term_cmd(client, message: Message, args):
    pref = getattr(client, "prefix", ".")
    if not args:
        return await message.edit(
            f"➡️ Terminal\n"
            f"{pref}term <command>"
        )

    cmd = " ".join(args)
    base_dir = os.getcwd()  # рабочая директория юзербота

    # оболочка для выполнения команды в ограниченной директории
    shell_cmd = f"cd {base_dir} && {cmd}"

    proc = await asyncio.create_subprocess_shell(
        shell_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    out = (stdout or b"").decode(errors="ignore").strip()
    err = (stderr or b"").decode(errors="ignore").strip()

    text = f"$ {cmd}\n\n"

    if out:
        text += f"stdout:\n{out}\n\n"
    if err:
        text += f"stderr:\n{err}\n\n"

    text += f"exit code: {proc.returncode}"

    if len(text) > 4000:
        text = text[:4000]

    await message.edit(text)


def register(app, commands, module_name):
    commands["term"] = {"func": term_cmd, "module": module_name}