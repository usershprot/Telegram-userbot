import os
import json
import time
import subprocess
import requests
import psutil
from telethon import events
from telethon.tl.types import InputMessagesFilterEmpty

HAS_PSUTIL = True

def upload_to_telegraph(image_url):
    """Загружает изображение на Telegraph и возвращает URL"""
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return None

        files = {'file': ('image.jpg', response.content, 'image/jpeg')}
        upload = requests.post('https://telegra.ph/upload', files=files, timeout=10)

        if upload.status_code == 200:
            result = upload.json()
            if isinstance(result, list) and len(result) > 0:
                return f"https://telegra.ph{result[0]['src']}"
    except:
        pass
    return None


async def info_cmd(event, client, args):
    """Информация о юзерботе"""

    me = await client.get_me()
    owner_name = f"{me.first_name or ''} {me.last_name or ''}".strip() or "Unknown"

    # Загружаем конфиг
    config_path = f"config-{me.id}.json"
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            pass

    prefix = config.get("prefix", ".")
    quote_media = config.get("info_quote_media", False)
    banner_url = config.get("info_banner_url", "")
    invert_media = config.get("info_invert_media", True)

    # Git branch
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except:
        branch = "unknown"

    # Uptime
    start_time = getattr(client, "start_time", time.time())
    uptime_seconds = int(time.time() - start_time)
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = " ".join([f"{days}д" if days else "",
                           f"{hours}ч" if hours else "",
                           f"{minutes}м" if minutes else "",
                           f"{seconds}с"]).strip()

    # RAM
    try:
        process = psutil.Process()
        ram_usage_mb = process.memory_info().rss / (1024 * 1024)
        ram_usage_str = f"{ram_usage_mb:.1f} MB"
    except:
        ram_usage_str = "N/A"

    # Hostname
    try:
        hostname = subprocess.check_output(["hostname"]).decode().strip()
    except:
        hostname = os.uname().nodename if hasattr(os, "uname") else "Unknown"

    # Формируем текст
    info_text = f"""<b>🔥 Forelka Userbot</b>

<b>👤 Владелец:</b> {owner_name}
<b>🌿 Branch:</b> {branch}
<b>⚙️ Prefix:</b> «{prefix}»
<b>⏱ Uptime:</b> {uptime_str}
<b>💾 RAM usage:</b> {ram_usage_str}
<b>🖥 Host:</b> {hostname}"""

    # Проверка баннера
    is_web_url = banner_url.startswith(("http://", "https://")) if banner_url else False
    is_local_file = os.path.exists(banner_url) if banner_url and not is_web_url else False

    try:
        await event.delete()
    except:
        pass

    try:
        if quote_media and is_web_url:
            # Quote media режим
            text_with_preview = f'<a href="{banner_url}">&#8288;</a>\n{info_text}'
            await client.send_message(
                event.chat_id,
                text_with_preview,
                parse_mode="html",
                link_preview=True
            )
        elif is_local_file or (is_web_url and not quote_media):
            # Фото баннера
            await client.send_file(
                event.chat_id,
                banner_url,
                caption=info_text,
                parse_mode="html"
            )
        else:
            # Просто текст
            await client.send_message(
                event.chat_id,
                info_text,
                parse_mode="html"
            )
    except:
        await client.send_message(event.chat_id, info_text, parse_mode="html")


async def setinfobanner_cmd(event, client, args):
    """Настройка баннера и quote media"""
    me = await client.get_me()
    config_path = f"config-{me.id}.json"
    config = {"prefix": "."}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except:
            pass

    if not args:
        quote_media = config.get("info_quote_media", False)
        banner_url = config.get("info_banner_url", "не установлен")
        invert_media = config.get("info_invert_media", True)

        await event.respond(
            f"<b>Info Banner Settings</b>\n\n"
            f"<b>Quote Media:</b> {'✅ Enabled' if quote_media else '❌ Disabled'}\n"
            f"<b>Invert Media:</b> {'✅ ON (сверху)' if invert_media else '❌ OFF (снизу)'}\n"
            f"<b>Banner URL:</b> {banner_url}\n\n"
            f"<b>Команды:</b>\n"
            f".setinfobanner [url] - установить URL баннера\n"
            f".setinfobanner quote [on/off] - quote media режим\n"
            f".setinfobanner invert [on/off] - превью сверху/снизу\n"
            f".setinfobanner clear - удалить настройки",
            parse_mode="html"
        )
        return

    cmd = args[0].lower()
    if cmd == "invert":
        if len(args) < 2:
            return await event.respond(".setinfobanner invert [on/off]")
        state = args[1].lower()
        if state in ["on", "true", "1", "да", "yes"]:
            config["info_invert_media"] = True
        elif state in ["off", "false", "0", "нет", "no"]:
            config["info_invert_media"] = False
        else:
            return await event.respond("Неверное значение. Используйте: on/off")
        with open(config_path, "w") as f: json.dump(config, f, indent=4)
        await event.respond(f"Invert Media {'ON' if config['info_invert_media'] else 'OFF'}")
    elif cmd == "quote":
        if len(args) < 2:
            return await event.respond(".setinfobanner quote [on/off]")
        state = args[1].lower()
        if state in ["on", "true", "1", "да", "yes"]:
            config["info_quote_media"] = True
        elif state in ["off", "false", "0", "нет", "no"]:
            config["info_quote_media"] = False
        else:
            return await event.respond("Неверное значение. Используйте: on/off")
        with open(config_path, "w") as f: json.dump(config, f, indent=4)
        await event.respond(f"Quote Media {'ON' if config.get('info_quote_media', False) else 'OFF'}")
    elif cmd == "clear":
        for key in ["info_banner_url", "info_quote_media", "info_invert_media"]:
            config.pop(key, None)
        with open(config_path, "w") as f: json.dump(config, f, indent=4)
        await event.respond("Настройки баннера удалены")
    else:
        banner_url = args[0]
        if not (banner_url.startswith(("http://", "https://")) or os.path.exists(banner_url)):
            return await event.respond("Неверный URL или файл не найден")
        config["info_banner_url"] = banner_url
        with open(config_path, "w") as f: json.dump(config, f, indent=4)
        await event.respond(f"Баннер установлен: {banner_url}")


def register(client, commands):
    commands["info"] = info_cmd
    commands["setinfobanner"] = setinfobanner_cmd