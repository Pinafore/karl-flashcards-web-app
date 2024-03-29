"""add repetition model, studyset type enum values

Revision ID: 7e18d411320e
Revises: f007a4240a14
Create Date: 2023-10-28 23:20:23.085384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e18d411320e'
down_revision = 'f007a4240a14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Rename the old enum
    op.execute("ALTER TYPE repetition ADD VALUE 'fsrs'")
    op.execute("ALTER TYPE repetition ADD VALUE 'karlAblation'")

    # Create a new enum with the desired values
    repetition = sa.Enum('leitner', 'karl', 'sm2', 'karl100', 'karl50', 'karl85', 'settles', 'fsrs', 'karlAblation', name='repetition')

    # For studyset.repetition_model column:
    # Create a temporary column with the new enum type
    op.add_column('studyset', sa.Column('repetition_model', repetition, nullable=True))
    op.execute("""
    UPDATE studyset
    SET repetition_model = "user".repetition_model
    FROM "user"
    WHERE studyset.user_id = "user".id
    """)

    # As we haven't had test deck assignments stored this way in the past, we can just do this!
    op.add_column('user_deck', sa.Column('temp_repetition_model_override', repetition, nullable=True))

    settype_enum = sa.Enum('test', 'post_test', 'normal', name='settype')
    settype_enum.create(op.get_bind())

    # Add the new set_type column with default as 'normal'
    op.add_column('studyset', sa.Column('set_type', settype_enum, nullable=True, server_default='normal'))

    # Migrate the data from is_test to set_type
    op.execute("""
    UPDATE studyset 
    SET set_type = CASE 
        WHEN is_test = True THEN 'test'::settype 
        ELSE 'normal'::settype 
    END
    """)

    # drop the is_test column and remove/add indices
    op.drop_index('ix_studyset_is_test', table_name='studyset')
    op.drop_column('studyset', 'is_test')
    op.create_index(op.f('ix_studyset_set_type'), 'studyset', ['set_type'], unique=False)
    
    # add user_deck column `completed`
    op.add_column('user_deck', sa.Column('completed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Drop the user_deck column `completed`
    op.drop_column('user_deck', 'completed')

    # Drop the new set_type column and its index from studyset
    op.drop_index(op.f('ix_studyset_set_type'), table_name='studyset')
    op.drop_column('studyset', 'set_type')

    # Re-add the is_test column and its index to studyset
    op.add_column('studyset', sa.Column('is_test', sa.Boolean(), nullable=True))
    op.create_index('ix_studyset_is_test', 'studyset', ['is_test'], unique=False)

    # Migrate the data from set_type back to is_test (assuming only 'test' and 'normal' were used in set_type)
    op.execute("UPDATE studyset SET is_test = CASE WHEN set_type = 'test'::settype THEN True ELSE False END")
    sa.Enum(name='settype').drop(op.get_bind())

    # Drop the repetition_model column from studyset
    op.drop_column('studyset', 'repetition_model')

    # ### end Alembic commands ###

