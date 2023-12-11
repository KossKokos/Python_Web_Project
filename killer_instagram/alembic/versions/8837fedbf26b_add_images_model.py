"""add_images_model

Revision ID: 8837fedbf26b
Revises: 
Create Date: 2023-12-11 23:57:28.678662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8837fedbf26b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.CheckConstraint("role IN ('admin', 'moderator', 'user')", name='check_valid_role'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('images_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('upload_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('public_id', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users_table.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comments_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(length=150), nullable=False),
    sa.Column('crated_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['images_table.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=30), nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['images_table.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tag')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags_table')
    op.drop_table('comments_table')
    op.drop_table('images_table')
    op.drop_table('users_table')
    # ### end Alembic commands ###
