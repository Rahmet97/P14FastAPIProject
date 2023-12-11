"""edited category table

Revision ID: 44eedfdb165e
Revises: 9484c4f093de
Create Date: 2023-12-11 11:33:50.669236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44eedfdb165e'
down_revision = '9484c4f093de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uniqNC', 'category', ['name', 'category'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uniqNC', 'category', type_='unique')
    # ### end Alembic commands ###
