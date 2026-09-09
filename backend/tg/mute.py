import os
import json
from datetime import timedelta

from dotenv import load_dotenv

from aiogram import Router, types, Bot
from aiogram import F
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError


router = Router()

load_dotenv()
admin_list = [str(a) for a in json.loads(os.getenv("ADMIN_ID") or "[]")]

# Мьют разрешён на время от 10 до 60 минут
MUTE_MIN_MINUTES = 10
MUTE_MAX_MINUTES = 60

# Пользователи, которым команда !mute недоступна
MUTE_BLOCKED_IDS = {512563919}


# ---функционал для мьюта пользователя---
@router.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def get_id_user_for_muted(message: Message, bot: Bot):
    if not message.text or message.text.split()[0] != '!mute':
        return

    if message.from_user.id in MUTE_BLOCKED_IDS:
        await message.answer("Извините, для вас функция недоступна, вы лох!")
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            f"Укажите время в минутах: !mute <{MUTE_MIN_MINUTES}-{MUTE_MAX_MINUTES}>"
        )
        return

    try:
        minutes = int(parts[1])
    except ValueError:
        await message.answer("Время нужно указать числом, в минутах")
        return

    if not MUTE_MIN_MINUTES <= minutes <= MUTE_MAX_MINUTES:
        await message.answer(
            f"Мьют возможен минимум на {MUTE_MIN_MINUTES}, максимум на {MUTE_MAX_MINUTES} минут"
        )
        return

    target = message.reply_to_message.from_user
    if target is None:
        await message.answer("Не понял, кого мьютить")
        return

    if str(target.id) in admin_list:
        await message.answer("Ага соси приколист!")
        return

    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=timedelta(minutes=minutes)
        )
    except TelegramAPIError:
        await message.answer("Не получилось замутить — проверь права бота в чате")
        return

    await message.answer(f"🔇 Пользователь {target.full_name} замучен на {minutes} минут")
