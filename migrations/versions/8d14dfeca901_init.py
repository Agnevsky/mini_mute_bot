"""init

Revision ID: 8d14dfeca901
Revises: 
Create Date: 2026-03-12 16:43:30.419633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d14dfeca901'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tg_id', sa.BigInteger(), nullable=False),
        sa.Column('tg_name', sa.String(), nullable=False),
        sa.Column('tg_username', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tg_id')
    )
    op.create_table('tournaments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('players_id', sa.Integer(), nullable=False),
        sa.Column('players_command', sa.String(), nullable=True),
        sa.Column('players_name', sa.String(), nullable=True),
        sa.Column('games', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('games_win', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('games_lose', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('win_extra_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lose_extra_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('missed_goals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score_goals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('different_goals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('win_shootout', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lose_shootout', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['players_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player1', sa.String(), nullable=False),
        sa.Column('player2', sa.String(), nullable=False),
        sa.Column('score1', sa.Integer(), nullable=False),
        sa.Column('score2', sa.Integer(), nullable=False),
        sa.Column('is_extra_time', sa.Boolean(), nullable=False),
        sa.Column('is_shootout', sa.Boolean(), nullable=True),
        sa.Column('team1', sa.String(), nullable=True),
        sa.Column('team2', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player1_id', sa.Integer(), nullable=False),
        sa.Column('player2_id', sa.Integer(), nullable=False),
        sa.Column('score1', sa.Integer(), nullable=False),
        sa.Column('score2', sa.Integer(), nullable=False),
        sa.Column('is_extra_time', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['player1_id'], ['tournaments.id']),
        sa.ForeignKeyConstraint(['player2_id'], ['tournaments.id']),
        sa.PrimaryKeyConstraint('id')
    )
