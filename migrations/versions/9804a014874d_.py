"""empty message

Revision ID: 9804a014874d
Revises: c05b4e7cce0e
Create Date: 2020-05-05 09:56:01.699380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9804a014874d'
down_revision = 'c05b4e7cce0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
