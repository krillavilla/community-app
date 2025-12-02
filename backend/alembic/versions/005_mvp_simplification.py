"""MVP simplification - remove complex tables, add core social features

Revision ID: 005_mvp_simplification
Revises: 004_add_lifecycle_engine
Create Date: 2025-11-26 04:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_mvp_simplification'
down_revision = '004_lifecycle'
branch_labels = None
depends_on = None


def upgrade():
    # Get connection to check for existing tables
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # ===== DROP COMPLEX TABLES FIRST =====
    # Drop these early to avoid foreign key conflicts
    tables_to_drop = ['climate_readings', 'pollination_events', 'nutrients', 'fences', 'roots', 'soil']
    for table_name in tables_to_drop:
        if table_name in existing_tables:
            op.drop_table(table_name)
    
    # ===== CREATE MVP TABLES =====
    
    # Posts table (simplified from seeds)
    if 'posts' not in existing_tables:
        op.create_table('posts',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('caption', sa.Text, nullable=True),
            sa.Column('video_url', sa.String(512), nullable=True),
            sa.Column('thumbnail_url', sa.String(512), nullable=True),
            sa.Column('duration_seconds', sa.Integer, nullable=True),
            sa.Column('view_count', sa.Integer, nullable=False, default=0),
            sa.Column('like_count', sa.Integer, nullable=False, default=0),
            sa.Column('comment_count', sa.Integer, nullable=False, default=0),
            sa.Column('share_count', sa.Integer, nullable=False, default=0),
            # Privacy: public or friends_only for MVP
            sa.Column('is_public', sa.Boolean, nullable=False, default=True),
            # Expiration: 24 hours from creation
            sa.Column('expires_at', sa.DateTime, nullable=False),
            sa.Column('soft_deleted', sa.Boolean, nullable=False, default=False),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
        )
    
    # MVP Comments table (separate from Flourish comments)
    if 'mvp_comments' not in existing_tables:
        op.create_table('mvp_comments',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('content', sa.Text, nullable=False),
            sa.Column('upvote_count', sa.Integer, nullable=False, default=0),
            sa.Column('downvote_count', sa.Integer, nullable=False, default=0),
            # Expiration: 7 days from creation
            sa.Column('expires_at', sa.DateTime, nullable=False),
            sa.Column('soft_deleted', sa.Boolean, nullable=False, default=False),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
        )
    
    # Likes table
    if 'likes' not in existing_tables:
        op.create_table('likes',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint('post_id', 'user_id', name='uq_post_user_like')
        )
    
    # Comment votes table - may already exist from migration 001
    # Drop it first if it exists with old schema, then recreate
    if 'comment_votes' in existing_tables:
        op.drop_table('comment_votes')
    
    op.create_table('comment_votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('comment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mvp_comments.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('vote_type', sa.String(10), nullable=False),  # 'up' or 'down'
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('comment_id', 'user_id', name='uq_comment_user_vote')
    )
    
    # Follows table
    if 'follows' not in existing_tables:
        op.create_table('follows',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('follower_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('following_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint('follower_id', 'following_id', name='uq_follower_following')
        )


def downgrade():
    # Restore complex tables (recreate from previous migrations if needed)
    op.drop_table('follows')
    op.drop_table('comment_votes')
    op.drop_table('likes')
    op.drop_table('mvp_comments')
    op.drop_table('posts')
    
    # Note: Complex tables would need to be recreated from previous migrations
    # This is acceptable for MVP - we can always restore from git history
