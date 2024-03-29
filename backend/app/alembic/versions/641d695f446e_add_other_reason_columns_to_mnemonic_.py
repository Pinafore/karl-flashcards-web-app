"""Add other reason columns to Mnemonic table

Revision ID: 641d695f446e
Revises: e1488e104d80
Create Date: 2023-12-20 20:29:17.475127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '641d695f446e'
down_revision = 'e1488e104d80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mnemonic', sa.Column('is_bad_for_other_reason', sa.Boolean(), nullable=True))
    op.add_column('mnemonic', sa.Column('other_reason_text', sa.String(), nullable=True))
    op.alter_column('mnemonic', 'study_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('mnemonic', 'fact_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('mnemonic', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'mnemonic', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'mnemonic', type_='foreignkey')
    op.alter_column('mnemonic', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('mnemonic', 'fact_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('mnemonic', 'study_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('mnemonic', 'other_reason_text')
    op.drop_column('mnemonic', 'is_bad_for_other_reason')
    # ### end Alembic commands ###
