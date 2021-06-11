"""Add target recall setting

Revision ID: 03d8017f5307
Revises: ca02ff820178
Create Date: 2021-06-11 20:02:58.118767

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '03d8017f5307'
down_revision = 'ca02ff820178'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('recall_target', sa.SmallInteger(), nullable=False, server_default='-1'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'recall_target')
    # ### end Alembic commands ###
