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


async def create_tournament(session: AsyncSession):

    await session.execute(delete(Tournament))
    await session.commit()
    