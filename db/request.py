from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from db.models import User, Tournament
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
