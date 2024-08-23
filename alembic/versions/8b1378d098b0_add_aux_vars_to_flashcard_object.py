"""add aux vars to Flashcard object

Revision ID: 8b1378d098b0
Revises: 
Create Date: 2024-08-23 10:20:11.898094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b1378d098b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('flashcards', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_flashcards_id'), ['id'])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('flashcards', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_flashcards_id'), type_='unique')

    # ### end Alembic commands ###
