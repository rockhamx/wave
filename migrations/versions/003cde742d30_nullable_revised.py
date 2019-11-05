"""nullable revised

Revision ID: 003cde742d30
Revises: bd3edb608fd3
Create Date: 2019-11-05 00:24:21.224177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003cde742d30'
down_revision = 'bd3edb608fd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)

    # ### end Alembic commands ###