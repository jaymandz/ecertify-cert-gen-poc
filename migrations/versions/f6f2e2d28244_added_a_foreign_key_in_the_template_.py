"""Added a foreign key in the Template model pointing to CertificateType

Revision ID: f6f2e2d28244
Revises: bd1ad8cff219
Create Date: 2024-05-31 10:42:40.040382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6f2e2d28244'
down_revision = 'bd1ad8cff219'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('template', schema=None) as batch_op:
        batch_op.add_column(sa.Column('certificate_type', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'certificate_type', ['certificate_type'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('template', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('certificate_type')

    # ### end Alembic commands ###
