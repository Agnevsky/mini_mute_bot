from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger
from db.database import Base



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    tg_name: Mapped[str]
    tg_username: Mapped[str]
    name: Mapped[str] = mapped_column(nullable=True)

    tournaments: Mapped[list["Tournament"]] = relationship(back_populates="player")




class Tournament(Base):
    __tablename__ = 'tournaments'

    id: Mapped[int] = mapped_column(primary_key=True)

    players_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )
    players_command: Mapped[str] = mapped_column(nullable=True)
    players_name: Mapped[str] = mapped_column(nullable=True)
    games: Mapped[int] = mapped_column(default=0)
    games_win: Mapped[int] = mapped_column(default=0)
    games_lose: Mapped[int] = mapped_column(default=0)
    win_extra_time: Mapped[int] = mapped_column(default=0)
    lose_extra_time: Mapped[int] = mapped_column(default=0)
    score: Mapped[int] = mapped_column(default=0)
    missed_goals: Mapped[int] = mapped_column(default=0)
    score_goals: Mapped[int] = mapped_column(default=0)
    different_goals: Mapped[int] = mapped_column(default=0)

    player: Mapped["User"] = relationship(back_populates="tournaments")
