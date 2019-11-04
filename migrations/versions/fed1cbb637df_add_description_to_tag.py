"""add description to tag

Revision ID: fed1cbb637df
Revises: 6ac3384aa3c1
Create Date: 2019-11-04 18:30:12.839735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fed1cbb637df'
down_revision = '6ac3384aa3c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
