"""Add video features, expiration, and GDPR compliance

Revision ID: 001_video_gdpr
Revises: 
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '001_video_gdpr'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Flourish posts table updates for video support
    op.add_column('flourish_posts', sa.Column('video_url', sa.String(512), nullable=True))
    op.add_column('flourish_posts', sa.Column('thumbnail_url', sa.String(512), nullable=True))
    op.add_column('flourish_posts', sa.Column('duration_seconds', sa.Integer(), nullable=True))
    op.add_column('flourish_posts', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('flourish_posts', sa.Column('privacy_level', sa.String(50), nullable=True, server_default='public'))
    op.add_column('flourish_posts', sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('flourish_posts', sa.Column('screenshot_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('flourish_posts', sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create post_views table for analytics
    op.create_table(
        'post_views',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('flourish_posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('viewer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('watched_duration_seconds', sa.Integer(), nullable=False),
        sa.Column('completion_rate', sa.Float(), nullable=False),
        sa.Column('viewed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_screenshot', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('idx_post_views_post_id', 'post_views', ['post_id'])
    op.create_index('idx_post_views_viewer_id', 'post_views', ['viewer_id'])
    op.create_index('idx_post_views_viewed_at', 'post_views', ['viewed_at'])
    
    # Comments table updates for expiration and voting
    op.add_column('comments', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('comments', sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('downvotes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create comment_votes table
    op.create_table(
        'comment_votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('comment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vote_type', sa.String(10), nullable=False),  # 'up' or 'down'
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_comment_vote_user', 'comment_votes', ['comment_id', 'user_id'])
    op.create_index('idx_comment_votes_comment_id', 'comment_votes', ['comment_id'])
    
    # Create privacy_circles table
    op.create_table(
        'privacy_circles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('circle_name', sa.String(100), nullable=False),  # 'friends', 'close_friends', 'orchard'
        sa.Column('member_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_circle_member', 'privacy_circles', ['user_id', 'circle_name', 'member_id'])
    op.create_index('idx_privacy_circles_user_id', 'privacy_circles', ['user_id'])
    op.create_index('idx_privacy_circles_circle_name', 'privacy_circles', ['circle_name'])
    
    # Create direct_messages table
    op.create_table(
        'direct_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_dm_sender_id', 'direct_messages', ['sender_id'])
    op.create_index('idx_dm_recipient_id', 'direct_messages', ['recipient_id'])
    op.create_index('idx_dm_created_at', 'direct_messages', ['created_at'])
    
    # Users table updates for age verification and GDPR
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('age_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # Drop new tables
    op.drop_table('direct_messages')
    op.drop_table('privacy_circles')
    op.drop_table('comment_votes')
    op.drop_table('post_views')
    
    # Remove columns from flourish_posts
    op.drop_column('flourish_posts', 'soft_deleted')
    op.drop_column('flourish_posts', 'screenshot_count')
    op.drop_column('flourish_posts', 'view_count')
    op.drop_column('flourish_posts', 'privacy_level')
    op.drop_column('flourish_posts', 'expires_at')
    op.drop_column('flourish_posts', 'duration_seconds')
    op.drop_column('flourish_posts', 'thumbnail_url')
    op.drop_column('flourish_posts', 'video_url')
    
    # Remove columns from comments
    op.drop_column('comments', 'soft_deleted')
    op.drop_column('comments', 'downvotes')
    op.drop_column('comments', 'upvotes')
    op.drop_column('comments', 'expires_at')
    
    # Remove columns from users
    op.drop_column('users', 'soft_deleted')
    op.drop_column('users', 'age_verified')
    op.drop_column('users', 'date_of_birth')
