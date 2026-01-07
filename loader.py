import importlib.util
import os
import sys
import inspect
import requests
from telethon.tl.types import Message


def is_protected(name):
    return os.path.exists(f"modules/{name}.py") or name in ["loader", "main"]


async def dlm_cmd(client, message: Message, args):
    if len(args) < 2:
        return await message.edit("❗️ Usage: .dlm [url] [name]")

    url, name = args[0], args[1].lower()
    if is_protected(name):
        return await message.edit("❌ Access Denied")

    path = f"loaded_modules/{name}.py"
    await message.edit(f"⌛️ Downloading {name}...")

    try:
        r = requests.get(url, timeout=10)
        with open(path, "wb") as f:
            f.write(r.content)

        if load_module(client, name, "loaded_modules"):
            await message.edit(f"✅ Module {name} installed")
        else:
            await message.edit("❌ Load failed")
    except Exception as e:
        await message.edit(f"❌ Error: {e}")


async def lm_cmd(client, message: Message, args):
    if not message.reply_to_msg_id:
        out = "Modules:\n" + "\n".join([f" • {m}" for m in sorted(client.loaded_modules)])
        return await message.edit(out)

    doc = await client.get_messages(message.chat_id, ids=message.reply_to_msg_id)
    if not doc.media:
        return await message.edit(".py only")

    file_name = getattr(doc.media.document, "attributes", [{}])[0].file_name or "module.py"
    if not file_name.endswith(".py"):
        return await message.edit(".py only")

    name = (args[0] if args else file_name[:-3]).lower()
    if is_protected(name):
        return await message.edit("❌ Access Denied")

    path = f"loaded_modules/{name}.py"
    await message.edit(f"⬇️ Saving {name}...")

    try:
        await client.download_media(doc, file=path)
        if load_module(client, name, "loaded_modules"):
            await message.edit(f"✅ Module {name} loaded")
        else:
            await message.edit("❌ Load failed")
    except Exception as e:
        await message.edit(f"❌ Error: {e}")


async def ulm_cmd(client, message: Message, args):
    if not args:
        return await message.edit("❗️ Usage: .ulm [name]")

    name = args[0].lower()
    if is_protected(name):
        return await message.edit("❌ Access Denied")

    path = f"loaded_modules/{name}.py"
    if os.path.exists(path):
        unload_module(client, name)
        os.remove(path)
        await message.edit(f"✅ Module {name} deleted")
    else:
        await message.edit("❌ Not found")


async def ml_cmd(client, message: Message, args):
    if not args:
        return await message.edit("❗️ Usage: .ml [name]")

    name = args[0]
    path = f"loaded_modules/{name}.py"
    if not os.path.exists(path):
        return await message.edit("❌ Not found")

    await message.delete()
    await client.send_file(
        message.chat_id,
        path,
        caption=f"✅ Module: {name}"
    )


def load_module(app, name, folder):
    path = os.path.abspath(os.path.join(folder, f"{name}.py"))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)

        reg = getattr(mod, "register", None)
        if reg:
            sig = inspect.signature(reg)
            if len(sig.parameters) == 3:
                reg(app, app.commands, name)
            else:
                reg(app, app.commands)
            app.loaded_modules.add(name)
            return True
    except:
        return False
    return False


def unload_module(app, name):
    to_pop = [k for k, v in list(app.commands.items()) if v.get("module") == name]
    for k in to_pop:
        app.commands.pop(k)
    app.loaded_modules.discard(name)
    if name in sys.modules:
        del sys.modules[name]


def load_all(app):
    app.commands.update({
        "dlm": {"func": dlm_cmd, "module": "loader"},
        "lm":  {"func": lm_cmd,  "module": "loader"},
        "ulm": {"func": ulm_cmd, "module": "loader"},
        "ml":  {"func": ml_cmd,  "module": "loader"}
    })
    app.loaded_modules.add("loader")

    for d in ["modules", "loaded_modules"]:
        if not os.path.exists(d):
            os.makedirs(d)
        for f in sorted(os.listdir(d)):
            if f.endswith(".py") and not f.startswith("_"):
                load_module(app, f[:-3], d)