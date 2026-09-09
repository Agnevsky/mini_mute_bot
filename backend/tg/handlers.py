from aiogram import Router
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from backend.db.request import get_game_results, update_game_record, rollback_game_result, add_game_result, update_game_result, update_table, get_tournament_table, add_user, get_user_by_tg_id, register_tournament, get_user_name, is_registered_in_tournament
from backend.db.database import async_session_maker

from backend.tg.export import create_tournament_excel
import backend.tg.keyboards as kb
from backend.tg.state import RegisterState
from backend.tg.parser import parse_results


router = Router()


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
                    await message.answer("Вы уже зарегистрированы в турнире!", reply_markup=kb.in_tournament)
                    return

        await state.set_state(RegisterState.waiting_team)
        await message.answer("За какую команду будете играть?")
        
    elif command.args == "edit_result":
        async with async_session_maker() as session:
            results = await get_game_results(session)
        
        if not results:
            await message.answer("Нет сыгранных игр")
            return
        
        text = "Выбери номер игры для редактирования:\n\n"
        for i, r in enumerate(results, 1):
            extra = " (ОТ)" if r.is_extra_time else " (БУЛ)" if r.is_shootout else ""
            text += f"{i}. {r.player1.title()} {r.score1}:{r.score2} {r.player2.title()}{extra}\n"
        
        await state.set_state(RegisterState.waiting_edit_choice)
        await state.update_data(results=[r.id for r in results])
        await message.answer(text)

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


# --- Получение результатов игры от пользователя ---
@router.message(RegisterState.waiting_result_game)
async def get_result_game(message: Message, state: FSMContext):
    results, errors = parse_results(message.text)

    if not results and errors:
        await message.answer(
            "Не смог распознать результат 😕\n"
            "Введите в формате: Имя игрока - Имя игрока 5 - 0\n"
            "Для овертайма добавьте 'от' в конце: Имя игрока - Имя игрока 5 - 4 от"
        )
        return

    success_list = []
    fail_list = []

    async with async_session_maker() as session:
        async with session.begin():
            for player1, player2, score1, score2, is_extra_time, is_shootout in results:
                success, not_found1, not_found2, team1, team2 = await update_game_result(
                    session, player1, player2, score1, score2, is_extra_time, is_shootout
                )
                extra = " (от)" if is_extra_time else " (бул)" if is_shootout else ""
                if success:
                    success_list.append(f"{player1.title()} {score1} - {score2} {player2.title()}{extra}")
                    await add_game_result(session, player1.title(), score1, score2, player2.title(), is_extra_time, is_shootout, team1, team2)
                else:
                    missing = ", ".join(filter(None, [not_found1, not_found2]))
                    fail_list.append(f"Не найден: {missing}")

    response = ""
    if success_list:
        response += "Внесено ✅\n" + "\n".join(success_list)
    if errors:
        response += "\n\nНе распознано 😕\n" + "\n".join(errors)
    if fail_list:
        response += "\n\nОшибки:\n" + "\n".join(fail_list)

    await message.answer(response)
    await state.clear()



# ---Регистрация в боте---
@router.message(RegisterState.waiting_name)
async def get_name(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    tg_name = message.from_user.first_name
    tg_username = message.from_user.username or ""
    name = message.text.title()

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
                p_command=team.upper(),
                p_name=(name or user.tg_name).title()
            )

    await state.clear()
    await message.answer("Вы зарегистрированы в турнире ✅", reply_markup=kb.in_tournament)

# ---очистка таблицы---
@router.callback_query(F.data.startswith("end_tournament"))
async def end_tournament(callback: CallbackQuery):
    async with async_session_maker() as session:
        players = await get_tournament_table(session)

    # сортировка
    players = sorted(players, key=lambda p: (
        -p.score,
        -(p.games_win - p.win_extra_time - p.win_shootout),  # победы в основное время
        -(p.games_win - p.win_shootout),                      # победы в основное время + ОТ
        -p.games_win,                                         # все победы
        -p.different_goals
    ))

    # отправляем файл
    file = create_tournament_excel(players)
    await callback.message.answer_document(
        BufferedInputFile(file.read(), filename="tournament.xlsx"),
        caption="Итоговая турнирная таблица 📊"
    )

    # очищаем таблицу
    async with async_session_maker() as session:
        async with session.begin():
            await update_table(session)

    
    await callback.message.answer('Таблица очищена, турнир завершён ✅')


# --- Редактирование результатов игры ---
@router.message(RegisterState.waiting_edit_choice)
async def get_edit_choice(message: Message, state: FSMContext):
    try:
        choice = int(message.text) - 1
    except ValueError:
        await message.answer("Введи число")
        return
    
    data = await state.get_data()
    result_ids = data.get("results", [])
    
    if choice < 0 or choice >= len(result_ids):
        await message.answer("Такого номера нет")
        return
    
    await state.update_data(edit_id=result_ids[choice])
    await state.set_state(RegisterState.waiting_edit_result)
    await message.answer(
        "Введи новый результат в формате:\n"
        "Имя игрока - Имя игрока 5 - 0\n"
        "Для овертайма добавь 'от' в конце"
    )


@router.message(RegisterState.waiting_edit_result)
async def apply_edit_result(message: Message, state: FSMContext):
    results, errors = parse_results(message.text)
    
    if not results or errors:
        await message.answer("Не смог распознать результат 😕")
        return
    
    data = await state.get_data()
    edit_id = data.get("edit_id")
    
    player1, player2, score1, score2, is_extra_time, is_shootout = results[0]
    
    async with async_session_maker() as session:
        async with session.begin():
            # откатываем старую статистику
            await rollback_game_result(session, edit_id)
            # применяем новую
            success, not_found1, not_found2, team1, team2 = await update_game_result(
                session, player1, player2, score1, score2, is_extra_time, is_shootout
                )
            if success:
                await update_game_record(session, edit_id, player1.title(), player2.title(), score1, score2, is_extra_time, is_shootout, team1, team2)
    
    if success:
        extra = " (ОТ)" if is_extra_time else " (БУЛ)" if is_shootout else ""
        await message.answer(f"Результат обновлён ✅\n{player1.title()} {score1}:{score2} {player2.title()}{extra}")
    else:
        await message.answer("Ошибка — игрок не найден ❌")
    
    await state.clear()
