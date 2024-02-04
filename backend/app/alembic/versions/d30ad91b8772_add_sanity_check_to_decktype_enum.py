"""Add sanity_check to DeckType enum

Revision ID: d30ad91b8772
Revises: 7a19b60fa20c
Create Date: 2024-01-30 01:49:17.765232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd30ad91b8772'
down_revision = '7a19b60fa20c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE decktype ADD VALUE 'sanity_check' AFTER 'public_mnemonic'")
    pass


def downgrade():
    pass
