"""add is_test to deck, partial index

Revision ID: 61dba6b62053
Revises: bcd5eab43566
Create Date: 2022-05-14 18:45:16.313435

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '61dba6b62053'
down_revision = 'bcd5eab43566'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deck', sa.Column('is_test', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index('ix_deck_is_test', 'deck', ['is_test'], unique=True, postgresql_where=sa.text('is_test = true'))
    op.drop_constraint('studyset_deck_id_fkey', 'studyset', type_='foreignkey')
    op.create_foreign_key(None, 'studyset', 'deck', ['deck_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'studyset', type_='foreignkey')
    op.create_foreign_key('studyset_deck_id_fkey', 'studyset', 'fact', ['deck_id'], ['fact_id'])
    op.drop_index('ix_deck_is_test', table_name='deck')
    op.drop_column('deck', 'is_test')
    # ### end Alembic commands ###