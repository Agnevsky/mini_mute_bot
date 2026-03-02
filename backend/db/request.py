from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from backend.db.models import User, Tournament
from sqlalchemy.ext.asyncio import AsyncSession


async def add_user(session: AsyncSession, tg_id: int, name: str, tg_name: str, tg_username: str):
    
    stmt = (
        insert(User)
        .values(
            tg_id=tg_id,
            tg_name=tg_name,
            tg_username=tg_username,
            name=name
        )
        .on_conflict_do_nothing(
            index_elements=["tg_id"]
        )
    )

    await session.execute(stmt)
    await session.commit()


async def get_user_by_tg_id(session: AsyncSession, tg_id: int):
    result = await session.execute(
        select(User).where(User.tg_id == tg_id)
    )
    return result.scalar_one_or_none()


async def get_user_name(session: AsyncSession, tg_id: int):
    name = await session.execute(select(User.name).where(User.tg_id == tg_id))
    return name.scalar_one_or_none()


async def update_table(session: AsyncSession):

    await session.execute(delete(Tournament))
    await session.commit()


async def register_tournament(
    session: AsyncSession,
    user_id: int,
    p_command: str,
    p_name: str
):
    data = insert(Tournament).values(
        players_id=user_id,
        players_name=p_name,
        players_command=p_command
    )

    await session.execute(data)


async def is_registered_in_tournament(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(
        select(Tournament).where(Tournament.players_id == user_id)
    )
    return result.scalars().first() is not None


async def get_tournament_table(session):
    result = await session.execute(select(Tournament))
    return result.scalars().all()


async def update_game_result(session, player1_name: str, player2_name: str, score1: int, score2: int, is_extra_time: bool):
    """Обновляет статистику обоих игроков после матча"""

    # Ищем игроков по имени в турнирной таблице (players_name)
    r1 = await session.execute(select(Tournament).where(Tournament.players_name.ilike(player1_name)))
    r2 = await session.execute(select(Tournament).where(Tournament.players_name.ilike(player2_name)))

    t1 = r1.scalar_one_or_none()
    t2 = r2.scalar_one_or_none()

    if not t1 or not t2:
        return None, player1_name if not t1 else None, player2_name if not t2 else None

    # Обновляем статистику
    t1.games += 1
    t2.games += 1

    t1.score_goals += score1
    t1.missed_goals += score2
    t1.different_goals = t1.score_goals - t1.missed_goals

    t2.score_goals += score2
    t2.missed_goals += score1
    t2.different_goals = t2.score_goals - t2.missed_goals

    if is_extra_time:
        if score1 > score2:
            t1.games_win += 1
            t1.win_extra_time += 1
            t1.score += 2
            t2.games_lose += 1
            t2.lose_extra_time += 1
            t2.score += 1
        else:
            t2.games_win += 1
            t2.win_extra_time += 1
            t2.score += 2
            t1.games_lose += 1
            t1.lose_extra_time += 1
            t1.score += 1
    else:
        if score1 > score2:
            t1.games_win += 1
            t1.score += 3
            t2.games_lose += 1
        elif score2 > score1:
            t2.games_win += 1
            t2.score += 3
            t1.games_lose += 1

    return True, None, None