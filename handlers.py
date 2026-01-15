from aiogram import Router, types, Bot
from datetime import timedelta
from aiogram import F
from aiogram.types import Message
from aiogram.filters import CommandStart
from datetime import datetime

router = Router()

@router.message(CommandStart())
async def say_hello(message: Message):
    await message.answer("Bot is ready")



@router.message(F.reply_to_message) 
async def get_id_user_for_muted(message: Message, bot: Bot):
    mute_command_list = message.text.split(' ') 
    if message.text.split(' ')[0] == '!mute' and len(mute_command_list) >= 1: 
       
        minutes = int(mute_command_list[1])
        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.full_name
        until_date = datetime.now() + timedelta(minutes=minutes)


        # используем message.bot, чтобы не зависеть от DI
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=until_date
        )

        await message.answer(f"🔇 Пользователь {name} замучен на {minutes} минут")
        print(f"Trying to mute user {user_id} in chat {message.chat.id} until {until_date}")


