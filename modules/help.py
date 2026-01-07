import sys
from telethon import events
from telethon.tl.types import Message

async def help_cmd(event: Message, client, args):
    pref = getattr(client, "prefix", ".")
    sys_mods, ext_mods = {}, {}

    for cmd_name, info in getattr(client, "commands", {}).items():
        mod_name = info.get("module", "unknown")
        mod_obj = sys.modules.get(mod_name)
        mod_path = getattr(mod_obj, "__file__", "") if mod_obj else ""
        target = ext_mods if "loaded_modules" in mod_path else sys_mods
        target.setdefault(mod_name, []).append(cmd_name)

    def format_mods(mods_dict):
        res = ""
        for mod, cmds in sorted(mods_dict.items()):
            cmds_str = " | ".join(f"{pref}{c}" for c in sorted(cmds))
            res += f"➡️ <b>{mod}</b> (<code>{cmds_str}</code>)\n"
        return res.strip()

    text = "👻 <b>Forelka Modules</b>\n\n"
    if sys_mods:
        text += f"<b>System:</b>\n<blockquote>{format_mods(sys_mods)}</blockquote>\n\n"
    if ext_mods:
        text += f"<b>External:</b>\n<blockquote>{format_mods(ext_mods)}</blockquote>"
    else:
        text += "<b>External:</b>\n<blockquote>No external modules</blockquote>"

    await event.edit(text, parse_mode="html")


def register(client, commands):
    commands["help"] = help_cmd