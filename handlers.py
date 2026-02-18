import os, json
from dotenv import load_dotenv

from datetime import timedelta, datetime

from aiogram import Router, types, Bot
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from state import RegisterState
from db.request import update_table, add_user, get_user_by_tg_id, register_tournament, get_user_name, is_registered_in_tournament
from db.database import async_session_maker
import keyboards as kb

router = Router()

load_dotenv()
admin_list = json.loads(os.getenv("ADMIN_ID"))

# ---Команда показывает меню если пользователь не зарегистрирован в боте---
@router.message(CommandStart())
async def say_hello(message: Message):

    tg_id = message.from_user.id

    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, tg_id)

    if user:
        # Уже зарегистрирован в боте
        await message.answer(
            "Меню", reply_markup=kb.in_tournament)
    else:
        await message.answer("Бот для мьюта свинки и проведения турниров", reply_markup=kb.keyboards)


# ---функционал для мьюта пользователя---
@router.message(F.reply_to_message)
async def get_id_user_for_muted(message: Message, bot: Bot):
    mute_command_list = message.text.split(' ')
    if message.text.split(' ')[0] == '!mute' and len(mute_command_list) >= 1:
        user_id = message.reply_to_message.from_user.id
        if admin_list[0] != str(user_id):
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


# ---Регистрация в боте-----------------------------------------------------------------
@router.callback_query(F.data.startswith("register_bot"))
async def clear_table_for_new_tournament(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id

    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, tg_id)

    if not user:
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
# -----------------------------------------------------------------------------


# Участие в турнире-------------------------------------------------------
@router.callback_query(F.data.startswith("join_tournament"))
async def join_the_tournament(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    async with async_session_maker() as session:
        async with session.begin():
            user = await get_user_by_tg_id(session, tg_id)

            if await is_registered_in_tournament(session, user.id):
                await callback.message.answer("Вы уже зарегистрированы в турнире!", reply_markup=kb.info_tournament)
                return
                
    await state.set_state(RegisterState.waiting_team)
    await callback.message.answer('За какую команду будете играть?')


@router.message(RegisterState.waiting_team)
async def get_team(message: Message, state: FSMContext):

    team = message.text
    tg_id = message.from_user.id

    async with async_session_maker() as session:
        async with session.begin():

            user = await get_user_by_tg_id(session, tg_id)
            name = await get_user_name(session, tg_id)

            await register_tournament(
                session,
                user_id=user.id,
                p_command=team,
                p_name=name
            )

    await state.clear()
    await message.answer("Вы зарегистрированы в турнире ✅", reply_markup=kb.info_tournament)

# ------------------------------------------------------------------------


# ---Обновление таблицы для нового турнира---
@router.callback_query(F.data.startswith("create_tournament"))
async def new_tournament(callback: CallbackQuery):
    async with async_session_maker() as session:
        async with session.begin():
            await update_table(session)
    await callback.message.answer('Таблица готова к использованию')
