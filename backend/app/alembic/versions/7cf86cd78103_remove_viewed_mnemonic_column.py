"""Remove viewed_mnemonic column

Revision ID: 7cf86cd78103
Revises: ab7e7e37b4cf
Create Date: 2023-12-26 22:03:52.005680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cf86cd78103'
down_revision = 'ab7e7e37b4cf'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('mnemonic', 'viewed_mnemonic')



def downgrade():
    op.add_column('mnemonic', sa.Column("viewed_mnemonic", sa.Boolean(), nullable=True))
