"""Add interactive_mnemonic to DeckType enum

Revision ID: 4911b9c37c7a
Revises: 0b0c9f4e82b9
Create Date: 2025-01-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4911b9c37c7a'
down_revision = '0b0c9f4e82b9'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'interactive_mnemonic' to the ENUM type in the database
    op.execute("ALTER TYPE decktype ADD VALUE 'interactive_mnemonic' AFTER 'public_mnemonic'")


def downgrade():
    # PostgreSQL doesn't support removing a value from an ENUM directly.
    # Downgrade logic is complex and depends on your requirements.
    # You might need to create a new ENUM without the 'interactive_mnemonic' value,
    # update the column to the new ENUM, and then drop the old ENUM.
    pass
