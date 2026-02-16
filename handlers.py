import os, json
from dotenv import load_dotenv

from datetime import timedelta, datetime

from aiogram import Router, types, Bot
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from state import RegisterState
from db.request import create_tournament, add_user, get_user_by_tg_id
from db.database import async_session_maker
import keyboards as kb

router = Router()

load_dotenv()
my_list = json.loads(os.getenv("ADMIN_ID"))

@router.message(CommandStart())
async def say_hello(message: Message):
    await message.answer("Бот для мьюта свинки, возможно будет расширяться, я имею в виду бота, а не свинью")


# ---функционал для мьюта пользователя---
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


# ---Команда для регистрации в боте, чтобы не запрашивать имя и прочее еще раз---
@router.message(Command('reg'))
async def register_on_bot(message: Message):
    tg_id = message.from_user.id

    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, tg_id)

    if user:
        # Уже зарегистрирован в боте
        await message.answer(
            "Вы уже зарегистрированы в боте")
    else:
        # Нужно зарегистрироваться в боте
        await message.answer(
            "Зарегистрируйтесь в боте",
            reply_markup=kb.register_bot
        )


@router.callback_query(F.data.startswith("register_bot"))
async def new_tournament(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(RegisterState.waiting_name)
    await callback.message.answer('Введите ваше имя')


@router.message(RegisterState.waiting_name)
async def get_name(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    tg_name = message.from_user.first_name
    tg_username = message.from_user.username
    name = message.text

    async with async_session_maker() as session:
        async with session.begin():
            await add_user(
                session,
                tg_id,
                name,
                tg_name, 
                tg_username
            )
    

    await state.clear()
    await message.answer("Вы зарегистрированы ✅")

# ---Регистрация в турнире----
@router.callback_query(F.data.startswith("register_tournament"))
async def new_tournament(callback: CallbackQuery):
    ...




# --- Команда для очистки таблицы---
@router.message(Command('new'))
async def new_command(message: Message):
    await message.answer('Обновите таблицу', reply_markup=kb.keyboards)


@router.callback_query(F.data.startswith("create_tournament"))
async def new_tournament(callback: CallbackQuery):
    
    async with async_session_maker() as session:
        async with session.begin():
            await create_tournament(session)

    await callback.message.answer('Таблица готова к использованию')