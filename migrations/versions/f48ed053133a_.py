"""empty message

Revision ID: f48ed053133a
Revises: df13fdd438bf
Create Date: 2020-05-05 20:36:26.564435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f48ed053133a'
down_revision = 'df13fdd438bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Artist', ['facebook_link'])
    op.create_unique_constraint(None, 'Artist', ['phone'])
    op.create_unique_constraint(None, 'Venue', ['phone'])
    op.create_unique_constraint(None, 'Venue', ['facebook_link'])
    op.create_unique_constraint(None, 'Venue', ['address'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Venue', type_='unique')
    op.drop_constraint(None, 'Venue', type_='unique')
    op.drop_constraint(None, 'Venue', type_='unique')
    op.drop_constraint(None, 'Artist', type_='unique')
    op.drop_constraint(None, 'Artist', type_='unique')
    # ### end Alembic commands ###