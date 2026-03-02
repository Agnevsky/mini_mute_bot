import os, json
from dotenv import load_dotenv

from datetime import timedelta, datetime

from aiogram import Router, types, Bot
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext

from backend.db.request import update_game_result, update_table, add_user, get_user_by_tg_id, register_tournament, get_user_name, is_registered_in_tournament
from backend.db.database import async_session_maker

import backend.tg.keyboards as kb
from backend.tg.state import RegisterState
from backend.tg.parser import parse_result


router = Router()

load_dotenv()
admin_list = json.loads(os.getenv("ADMIN_ID"))


# ---/start только в личке---
@router.message(CommandStart(), F.chat.type == "private")
async def say_hello(message: Message, command: CommandObject, state: FSMContext):
    tg_id = message.from_user.id

    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, tg_id)

    if command.args == "register_bot":
        if user:
            await message.answer("Вы уже зарегистрированы ✅", reply_markup=kb.in_tournament)
        else:
            await state.set_state(RegisterState.waiting_name)
            await message.answer("Введите ваше имя:")

    elif command.args == "join_tournament":
        if not user:
            await message.answer("Сначала зарегистрируйтесь в боте", reply_markup=kb.keyboards)
            return

        async with async_session_maker() as session:
            async with session.begin():
                if await is_registered_in_tournament(session, user.id):
                    await message.answer("Вы уже зарегистрированы в турнире!", reply_markup=kb.info_tournament)
                    return

        await state.set_state(RegisterState.waiting_team)
        await message.answer("За какую команду будете играть?")


    elif command.args == "result_game":
        await state.set_state(RegisterState.waiting_result_game)
        await message.answer('Жду результаты')
    


# ---Команда для показа меню в общем чате---
@router.message(Command('menu'))
async def show_menu(message: Message):
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, message.from_user.id)

    if user:
        await message.answer("Меню", reply_markup=kb.in_tournament)
    else:
        await message.answer("Меню", reply_markup=kb.keyboards)



# ---Функционал для внесения результатов в таблицу---
@router.message(RegisterState.waiting_result_game)
async def get_result_game(message: Message, state: FSMContext):
    parsed = parse_result(message.text)

    if not parsed:
        await message.answer(
            "Не смог распознать результат 😕\n"
            "Введите в формате: Илья - Андрей 5 - 0\n"
            "Для овертайма добавьте 'от' в конце: Илья - Андрей 5 - 4 от"
        )
        return

    player1, player2, score1, score2, is_extra_time = parsed

    async with async_session_maker() as session:
        async with session.begin():
            success, not_found1, not_found2 = await update_game_result(
                session, player1, player2, score1, score2, is_extra_time
            )

    if not success:
        missing = ", ".join(filter(None, [not_found1, not_found2]))
        await message.answer(f"Игрок(и) не найден(ы) в турнирной таблице: {missing}")
        return

    extra = " (овертайм)" if is_extra_time else ""
    await message.answer(
        f"Результат внесён ✅\n"
        f"{player1.title()} {score1} - {score2} {player2.title()}{extra}"
    )
    await state.clear()



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
            await message.answer(f"Ага соси приколист!")



# ---Регистрация в боте---
@router.message(RegisterState.waiting_name)
async def get_name(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    tg_name = message.from_user.first_name
    tg_username = message.from_user.username
    name = message.text

    async with async_session_maker() as session:
        async with session.begin():
            await add_user(session, tg_id, name, tg_name, tg_username)

    await state.clear()
    await message.answer("Вы зарегистрированы ✅", reply_markup=kb.in_tournament)


# ---Участие в турнире---
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


@router.callback_query(F.data.startswith())

# ---Обновление таблицы для нового турнира---
@router.callback_query(F.data.startswith("create_tournament"))
async def new_tournament(callback: CallbackQuery):
    async with async_session_maker() as session:
        async with session.begin():
            await update_table(session)
    await callback.message.answer('Таблица готова к использованию')
