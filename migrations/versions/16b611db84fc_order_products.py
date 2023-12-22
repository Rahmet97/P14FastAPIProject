"""order products

Revision ID: 16b611db84fc
Revises: 4db1f15e6c79
Create Date: 2023-12-22 11:47:01.028507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16b611db84fc'
down_revision = '4db1f15e6c79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_products',
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], )
    )
    op.drop_constraint('order_product_id_fkey', 'order', type_='foreignkey')
    op.drop_column('order', 'product_id')
    op.drop_column('order', 'count')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('order', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('order_product_id_fkey', 'order', 'product', ['product_id'], ['id'])
    op.drop_table('order_products')
    # ### end Alembic commands ###
