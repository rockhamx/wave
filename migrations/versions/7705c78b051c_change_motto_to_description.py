"""change motto to description

Revision ID: 7705c78b051c
Revises: fed1cbb637df
Create Date: 2019-11-04 20:23:11.066827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7705c78b051c'
down_revision = 'fed1cbb637df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('motto', new_column_name='description')
        # batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        # batch_op.drop_column('motto')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('description', new_column_name='motto')
        # batch_op.add_column(sa.Column('motto', sa.TEXT(), nullable=True))
        # batch_op.drop_column('description')

    # ### end Alembic commands ###
