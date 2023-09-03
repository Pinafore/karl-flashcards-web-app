"""add GIN indices

Revision ID: ffdf470fe0ba
Revises: c8bcaad53b52
Create Date: 2020-06-16 22:40:36.753058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffdf470fe0ba'
down_revision = 'c8bcaad53b52'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('idx_fact_fts'),
                    'fact',
                    [sa.text('to_tsvector(\'english\'::regconfig, text || \' \' || answer || \' \' || category || \' \' || identifier)')],
                    postgresql_using='gin')

def downgrade():
    op.drop_index(op.f('idx_fact_fts'), table_name='fact')
