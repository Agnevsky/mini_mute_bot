"""add teams to game_results

Revision ID: b9d1c8c09bb4
Revises: ea4b71d6f6c4
Create Date: 2026-03-09 16:09:28.568281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9d1c8c09bb4'
down_revision: Union[str, Sequence[str], None] = 'ea4b71d6f6c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('game_results', sa.Column('team1', sa.String(), nullable=True))
    op.add_column('game_results', sa.Column('team2', sa.String(), nullable=True))
    op.drop_column('game_results', 'created_at')

def downgrade():
    op.add_column('game_results', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.drop_column('game_results', 'team1')
    op.drop_column('game_results', 'team2')
