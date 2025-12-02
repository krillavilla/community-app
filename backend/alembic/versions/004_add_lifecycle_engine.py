"""add lifecycle engine fields

Revision ID: 004_lifecycle
Revises: 003_garden_system_core
Create Date: 2025-11-25

Adds lifecycle stage tracking to seeds:
- lifecycle_stage enum (seed, sprout, vine, fruit, compost)
- lifecycle_updated_at timestamp
- engagement_score for growth calculation
- expiry_date for automatic composting
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_lifecycle'
down_revision = '003_garden_system'
branch_labels = None
depends_on = None

# Create lifecycle stage enum
lifecycle_stage_enum = postgresql.ENUM(
    'seed', 'sprout', 'vine', 'fruit', 'compost',
    name='lifecycle_stage'
)

def upgrade():
    # Create enum type
    lifecycle_stage_enum.create(op.get_bind(), checkfirst=True)
    
    # Add lifecycle columns to seeds table
    op.add_column('seeds', sa.Column(
        'lifecycle_stage',
        lifecycle_stage_enum,
        nullable=False,
        server_default='seed'
    ))
    
    op.add_column('seeds', sa.Column(
        'lifecycle_updated_at',
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text('NOW()')
    ))
    
    op.add_column('seeds', sa.Column(
        'engagement_score',
        sa.Integer(),
        nullable=False,
        server_default='0'
    ))
    
    op.add_column('seeds', sa.Column(
        'expiry_date',
        sa.DateTime(timezone=True),
        nullable=True
    ))
    
    # Create index for efficient worker queries
    op.create_index(
        'idx_seeds_lifecycle_stage',
        'seeds',
        ['lifecycle_stage', 'lifecycle_updated_at']
    )

def downgrade():
    # Remove index and columns
    op.drop_index('idx_seeds_lifecycle_stage', 'seeds')
    op.drop_column('seeds', 'expiry_date')
    op.drop_column('seeds', 'engagement_score')
    op.drop_column('seeds', 'lifecycle_updated_at')
    op.drop_column('seeds', 'lifecycle_stage')
    
    # Drop enum type
    lifecycle_stage_enum.drop(op.get_bind(), checkfirst=True)
