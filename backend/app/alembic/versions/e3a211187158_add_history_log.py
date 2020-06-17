"""add history log

Revision ID: e3a211187158
Revises: b7b8acac9d4f
Create Date: 2020-06-17 19:38:00.388140

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e3a211187158'
down_revision = 'b7b8acac9d4f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("ALTER TYPE log ADD VALUE 'browser'")
    op.execute("ALTER TYPE log ADD VALUE 'get_facts'")
    op.execute("ALTER TYPE log ADD VALUE 'update_fact'")
    op.execute("ALTER TYPE log ADD VALUE 'mark'")
    op.execute("ALTER TYPE log ADD VALUE 'undo_suspend'")
    op.execute("ALTER TYPE log ADD VALUE 'undo_report'")
    op.execute("ALTER TYPE log ADD VALUE 'undo_mark'")
    op.execute("ALTER TYPE log ADD VALUE 'clear_report_or_suspend'")
    op.execute("ALTER TYPE log ADD VALUE 'assign_viewer'")


def downgrade():
    pass
