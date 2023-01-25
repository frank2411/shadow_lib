"""empty message

Revision ID: fb2ff0d058c9
Revises: 88e8d6f34142
Create Date: 2023-01-25 09:44:06.146433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb2ff0d058c9'
down_revision = '88e8d6f34142'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('has_been_returned', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'has_been_returned')
    # ### end Alembic commands ###
