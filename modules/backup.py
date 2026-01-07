import os
import zipfile
import json
from datetime import datetime

BACKUP_DIR = "backups"

def is_owner(client, user_id):
    """Проверяет является ли пользователь овнером"""
    config_path = f"config-{client.get_me().id}.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                owners = config.get("owners", [])
                if client.get_me().id not in owners:
                    owners.append(client.get_me().id)
                return user_id in owners
        except:
            pass
    return user_id == client.get_me().id

def ensure_backup_dir():
    """Создает папку для бекапов если её нет"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def get_files_to_backup():
    """Возвращает список файлов для бекапа"""
    files = []

    # Загруженные модули
    if os.path.exists("loaded_modules"):
        for f in os.listdir("loaded_modules"):
            if f.endswith(".py"):
                files.append(os.path.join("loaded_modules", f))

    # Конфигурационные файлы
    for f in os.listdir():
        if f.startswith("config-") and f.endswith(".json"):
            files.append(f)

    # База данных
    if os.path.exists("forelka.db"):
        files.append("forelka.db")

    return files

async def backup_cmd(event, client, args):
    """Создает бекап всех данных"""
    if not is_owner(client, event.sender_id):
        return await event.edit("❌ <b>Доступ запрещен</b>", parse_mode="html")

    ensure_backup_dir()
    await event.edit("⌛️ <b>Создание бекапа...</b>", parse_mode="html")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        files = get_files_to_backup()
        if not files:
            return await event.edit("❌ <b>Нет файлов для бекапа</b>", parse_mode="html")

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                zipf.write(file)

        size_mb = os.path.getsize(backup_path) / (1024 * 1024)

        caption = (
            f"✅ <b>Бекап создан!</b>\n\n"
            f"<b>Размер:</b> <code>{size_mb:.2f} MB</code>\n"
            f"<b>Файлов:</b> <code>{len(files)}</code>\n\n"
            f"<b>Содержимое:</b>\n" +
            "\n".join([f"• <code>{f}</code>" for f in sorted(files)[:10]])
        )
        if len(files) > 10:
            caption += f"\n... и ещё {len(files) - 10} файлов"

        await client.send_file(event.chat_id, backup_path, caption=caption, force_document=True)

    except Exception as e:
        await event.edit(f"❌ <b>Ошибка:</b> <code>{str(e)}</code>", parse_mode="html")


async def restore_cmd(event, client, args):
    """Восстанавливает данные из бекапа"""
    if not is_owner(client, event.sender_id):
        return await event.edit("❌ <b>Доступ запрещен</b>", parse_mode="html")

    ensure_backup_dir()
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".zip")]
    if not backups:
        return await event.edit("❌ <b>Нет доступных бекапов</b>\nСоздайте бекап командой: <code>.backup</code>", parse_mode="html")

    backup_name = args[0] if args and args[0].endswith(".zip") else (f"{args[0]}.zip" if args else sorted(backups)[-1])
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    if not os.path.exists(backup_path):
        return await event.edit(f"❌ <b>Бекап не найден:</b> <code>{backup_name}</code>", parse_mode="html")

    await event.edit(f"⌛️ <b>Восстановление из бекапа...</b>\n\n<code>{backup_name}</code>", parse_mode="html")

    try:
        if not os.path.exists("loaded_modules"):
            os.makedirs("loaded_modules")

        restored_files = []
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            for file in zipf.namelist():
                zipf.extract(file)
                restored_files.append(file)

        await event.edit(
            f"✅ <b>Бекап восстановлен!</b>\n\n"
            f"<b>Файл:</b> <code>{backup_name}</code>\n"
            f"<b>Восстановлено файлов:</b> <code>{len(restored_files)}</code>\n\n"
            f"❗️ <b>Перезапустите юзербот для применения изменений!</b>\n\n"
            f"<b>Восстановлено:</b>\n" +
            "\n".join([f"• <code>{f}</code>" for f in sorted(restored_files)]),
            parse_mode="html"
        )

    except Exception as e:
        await event.edit(f"❌ <b>Ошибка:</b> <code>{str(e)}</code>", parse_mode="html")


async def backups_cmd(event, client, args):
    """Показывает список доступных бекапов"""
    if not is_owner(client, event.sender_id):
        return await event.edit("❌ <b>Доступ запрещен</b>", parse_mode="html")

    ensure_backup_dir()
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".zip")]
    if not backups:
        return await event.edit("❌ <b>Нет доступных бекапов</b>\nСоздайте бекап командой: <code>.backup</code>", parse_mode="html")

    backups.sort(reverse=True)
    text = "👻 <b>Доступные бекапы</b>\n\n"

    for backup in backups:
        backup_path = os.path.join(BACKUP_DIR, backup)
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        try:
            date_str = backup.replace("backup_", "").replace(".zip", "")
            date_formatted = datetime.strptime(date_str, "%Y%m%d_%H%M%S").strftime("%d.%m.%Y %H:%M:%S")
        except:
            date_formatted = "Unknown"
        text += f"➡️ <code>{backup}</code>\n<b>Дата:</b> <code>{date_formatted}</code>\n<b>Размер:</b> <code>{size_mb:.2f} MB</code>\n\n"

    text += f"<b>Всего:</b> <code>{len(backups)}</code> бекапов\n"
    text += "<b>Команды:</b>\n<code>.backup</code> - создать бекап\n<code>.restore [name]</code> - восстановить\n<code>.backups</code> - список бекапов"

    await event.edit(text, parse_mode="html")


async def delbackup_cmd(event, client, args):
    """Удаляет бекап"""
    if not is_owner(client, event.sender_id):
        return await event.edit("❌ <b>Доступ запрещен</b>", parse_mode="html")

    if not args:
        return await event.edit("❗️ <b>Usage:</b> <code>.delbackup [name]</code>", parse_mode="html")

    backup_name = args[0] if args[0].endswith(".zip") else f"{args[0]}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    if not os.path.exists(backup_path):
        return await event.edit(f"❌ <b>Бекап не найден:</b> <code>{backup_name}</code>", parse_mode="html")

    try:
        os.remove(backup_path)
        await event.edit(f"✅ <b>Бекап удален:</b> <code>{backup_name}</code>", parse_mode="html")
    except Exception as e:
        await event.edit(f"❌ <b>Ошибка:</b> <code>{str(e)}</code>", parse_mode="html")


def register(client, commands):
    commands["backup"] = backup_cmd
    commands["restore"] = restore_cmd
    commands["backups"] = backups_cmd
    commands["delbackup"] = delbackup_cmd