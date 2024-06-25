"""Created the ecipient table

Revision ID: c5d469d2a600
Revises: 99c5f0446b0b
Create Date: 2024-06-25 14:20:29.765110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d469d2a600'
down_revision = '99c5f0446b0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('certificate_id', sa.Integer(), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('middle_name', sa.String(length=255), nullable=True),
    sa.Column('honorific', sa.String(length=255), nullable=True),
    sa.Column('suffix', sa.String(length=255), nullable=True),
    sa.Column('organization', sa.String(length=255), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['certificate_id'], ['certificate.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipient')
    # ### end Alembic commands ###
