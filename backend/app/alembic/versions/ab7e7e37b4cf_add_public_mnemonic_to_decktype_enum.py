"""Add public_mnemonic to DeckType enum

Revision ID: ab7e7e37b4cf
Revises: 641d695f446e
Create Date: 2023-12-26 18:36:28.043481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab7e7e37b4cf'
down_revision = '641d695f446e'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'public_mnemonic' to the ENUM type in the database
    op.execute("ALTER TYPE decktype ADD VALUE 'public_mnemonic'")

def downgrade():
    # PostgreSQL doesn't support removing a value from an ENUM directly.
    # Downgrade logic is complex and depends on your requirements.
    # You might need to create a new ENUM without the 'public_mnemonic' value,
    # update the column to the new ENUM, and then drop the old ENUM.
    pass