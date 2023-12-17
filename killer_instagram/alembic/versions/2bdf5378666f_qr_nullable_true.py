"""qr_nullable_true

Revision ID: 2bdf5378666f
Revises: 
Create Date: 2023-12-16 21:51:29.828406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bdf5378666f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transformed_image_links', 'qr_code_url',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.drop_constraint('transformed_image_links_transformation_url_key', 'transformed_image_links', type_='unique')
    op.drop_constraint('transformed_image_links_image_id_fkey', 'transformed_image_links', type_='foreignkey')
    op.create_foreign_key(None, 'transformed_image_links', 'images_table', ['image_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transformed_image_links', type_='foreignkey')
    op.create_foreign_key('transformed_image_links_image_id_fkey', 'transformed_image_links', 'images_table', ['image_id'], ['id'])
    op.create_unique_constraint('transformed_image_links_transformation_url_key', 'transformed_image_links', ['transformation_url'])
    op.alter_column('transformed_image_links', 'qr_code_url',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###
