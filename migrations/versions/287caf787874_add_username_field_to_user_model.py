"""Add username field to User model

Revision ID: 287caf787874
Revises: 3777d015357a
Create Date: 2024-11-27 15:44:50.662917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '287caf787874'
down_revision = '3777d015357a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')
    # ### end Alembic commands ###
