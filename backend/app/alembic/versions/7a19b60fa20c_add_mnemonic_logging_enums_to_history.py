"""Add mnemonic logging enums to history

Revision ID: 7a19b60fa20c
Revises: 7cf86cd78103
Create Date: 2024-01-16 19:50:47.878556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a19b60fa20c'
down_revision = '7cf86cd78103'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE log ADD VALUE 'mnemonic_learning_feedback'")
    op.execute("ALTER TYPE log ADD VALUE 'mnemonic_comparison_feedback'")
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
