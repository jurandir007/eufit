"""add shortened_urls and url_clicks tables

Revision ID: 2eab8df76ae1
Revises: 22454547edbf
Create Date: 2026-11-02 12:28:54.827535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2eab8df76ae1'
down_revision = '22454547edbf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('shortened_urls',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('original_url', sa.Text(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('clicks_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('shortened_urls', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_shortened_urls_code'), ['code'], unique=True)

    op.create_table('url_clicks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('shortened_url_id', sa.Integer(), nullable=False),
        sa.Column('clicked_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['shortened_url_id'], ['shortened_urls.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('url_clicks')
    with op.batch_alter_table('shortened_urls', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_shortened_urls_code'))
    op.drop_table('shortened_urls')
