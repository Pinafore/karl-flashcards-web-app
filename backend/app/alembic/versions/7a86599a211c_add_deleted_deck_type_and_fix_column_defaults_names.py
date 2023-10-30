"""add deleted deck type and fix column defaults names

Revision ID: 7a86599a211c
Revises: 7e18d411320e
Create Date: 2023-10-29 18:29:05.978179

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7a86599a211c'
down_revision = '7e18d411320e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE decktype ADD VALUE 'deleted'")
    op.alter_column('studyset', 'set_type',
               existing_type=postgresql.ENUM('test', 'post_test', 'normal', name='settype'),
               nullable=False,
               existing_server_default=sa.text("'normal'::settype"))
    op.alter_column('studyset', 'repetition_model',
               existing_type=postgresql.ENUM('leitner', 'sm2', 'karl100', 'karl50', 'karl85', 'karl', 'settles', 'fsrs', 'karlAblation', name='repetition'),
               nullable=False)
    op.alter_column('user_deck', 'temp_repetition_model_override', new_column_name='repetition_model_override')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_deck', 'repetition_model_override', new_column_name='temp_repetition_model_override')
    op.alter_column('studyset', 'repetition_model',
               existing_type=postgresql.ENUM('leitner', 'sm2', 'karl100', 'karl50', 'karl85', 'karl', 'settles', 'fsrs', 'karlAblation', name='repetition'),
               nullable=True)
    op.alter_column('studyset', 'set_type',
               existing_type=postgresql.ENUM('test', 'post_test', 'normal', name='settype'),
               nullable=True,
               existing_server_default=sa.text("'normal'::settype"))
    # ### end Alembic commands ###
