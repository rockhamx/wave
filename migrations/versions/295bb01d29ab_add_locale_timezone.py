"""add locale & timezone

Revision ID: 295bb01d29ab
Revises: 66e0f3344d0f
Create Date: 2019-11-02 21:05:11.691533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '295bb01d29ab'
down_revision = '66e0f3344d0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('locale', sa.String(length=8), nullable=True))
        batch_op.add_column(sa.Column('timezone', sa.String(length=8), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('timezone')
        batch_op.drop_column('locale')

    # ### end Alembic commands ###
