import os, json
from dotenv import load_dotenv
from aiogram import Router, types, Bot
from datetime import timedelta
from aiogram import F
from aiogram.types import Message
from aiogram.filters import CommandStart
from datetime import datetime

router = Router()

load_dotenv()
my_list = json.loads(os.getenv("ADMIN_ID"))

@router.message(CommandStart())
async def say_hello(message: Message):
    await message.answer("Бот для мьюта свинки, возможно будет расширяться, я имею в виду бота, а не свинью")



@router.message(F.reply_to_message)
async def get_id_user_for_muted(message: Message, bot: Bot):
    mute_command_list = message.text.split(' ')
    if message.text.split(' ')[0] == '!mute' and len(mute_command_list) >= 1:
        user_id = message.reply_to_message.from_user.id
        if my_list[0] != str(user_id):
            minutes = int(mute_command_list[1])
            name = message.reply_to_message.from_user.full_name
            until_date = datetime.now() + timedelta(minutes=minutes)


            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
                permissions=types.ChatPermissions(can_send_messages=False),
                until_date=until_date
            )

            await message.answer(f"🔇 Пользователь {name} замучен на {minutes} минут")

        else:
            await message.answer(f"Ага соси приколист! ")