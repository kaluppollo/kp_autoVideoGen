from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'areas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('primary_social', sa.String(), nullable=False),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('api_keys', sa.JSON(), nullable=True),
        sa.Column('default_min_duration_min', sa.Integer(), server_default='5', nullable=False),
        sa.Column('default_max_duration_min', sa.Integer(), server_default='10', nullable=False),
        sa.Column('languages', sa.JSON(), server_default='["en","it","fr","de","es","hi","zh"]', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'contents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('area_id', sa.Integer(), sa.ForeignKey('areas.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic_title', sa.Text(), nullable=False),
        sa.Column('micro_outline', sa.JSON(), nullable=True),
        sa.Column('transcript', sa.JSON(), nullable=True),
        sa.Column('duration_sec', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), server_default='draft', nullable=False),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('publish_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'schedule',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('content_id', sa.Integer(), sa.ForeignKey('contents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='pending', nullable=False),
        sa.Column('lock_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'media',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('content_id', sa.Integer(), sa.ForeignKey('contents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('section_order', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('path', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    op.create_table(
        'publish_queue',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('content_id', sa.Integer(), sa.ForeignKey('contents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_social', sa.String(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('cover_media_id', sa.Integer(), sa.ForeignKey('media.id'), nullable=True),
        sa.Column('clip_media_id', sa.Integer(), sa.ForeignKey('media.id'), nullable=True),
        sa.Column('status', sa.String(), server_default='pending', nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('publish_queue')
    op.drop_table('media')
    op.drop_table('schedule')
    op.drop_table('contents')
    op.drop_table('areas')