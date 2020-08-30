"""Add beta user and creation date to user

Revision ID: 98309991d026
Revises: fdb5d50f8331
Create Date: 2020-08-27 17:32:52.541227

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '98309991d026'
down_revision = 'fdb5d50f8331'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('beta_user', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('create_date', sa.TIMESTAMP(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'create_date')
    op.drop_column('user', 'beta_user')
    # ### end Alembic commands ###