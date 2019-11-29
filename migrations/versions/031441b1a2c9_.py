"""empty message

Revision ID: 031441b1a2c9
Revises: 
Create Date: 2019-11-21 23:20:22.707271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '031441b1a2c9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###