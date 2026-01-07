from telethon.tl.types import Message

def get_command_from_message(message: Message, prefix: str):
    if not message.message or not message.message.startswith(prefix):
        return None

    parts = message.message[len(prefix):].split()
    if not parts:
        return None

    return parts[0].lower(), parts[1:]