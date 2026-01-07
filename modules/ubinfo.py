from telethon.tl.types import Message

async def ubinfo_cmd(client, message: Message, args):
    text = (
        "Forelka Userbot\n\n"
        "Channel: @forelkauserbots\n"
        "Modules: @forelkausermodules\n"
        "Support: @forelka_support"
    )
    await message.edit(text, link_preview=False)

def register(app, commands, module_name):
    commands["forelka"] = {"func": ubinfo_cmd, "module": module_name}