"""Add column last_test_date to User

Revision ID: e0fa43c0f38d
Revises: 6c00659b79c1
Create Date: 2021-12-26 04:54:06.897334

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0fa43c0f38d'
down_revision = '6c00659b79c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_test_date', sa.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_test_date')
    # ### end Alembic commands ###
