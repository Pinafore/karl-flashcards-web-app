"""karl -> karl100

Revision ID: ca02ff820178
Revises: 98309991d026
Create Date: 2020-10-07 05:25:05.042850

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ca02ff820178'
down_revision = '98309991d026'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("ALTER TYPE repetition RENAME VALUE 'karl' TO 'karl100'")


def downgrade():
    op.execute("COMMIT")
    op.execute("ALTER TYPE repetition RENAME VALUE 'karl100' TO 'karl'")
