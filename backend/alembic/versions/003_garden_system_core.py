"""Garden System Core - Seeds, Vines, Soil, Fences

Revision ID: 003_garden_system
Revises: 002_allow_null_emails
Create Date: 2025-11-25

This migration creates the core Garden System tables:
- seeds (posts/videos with lifecycle)
- vines (users with health metrics)
- soil (comments as nutrients)
- nutrients (votes on comments)
- fences (privacy circles)
- roots (direct messages)
- pollination_events (discovery tracking)
- climate_readings (community health)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = '003_garden_system'
down_revision = '002_allow_null_emails'
branch_labels = None
depends_on = None


def upgrade():
    # Create ENUM types for lifecycle states (only if they don't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE seed_state AS ENUM ('planted', 'sprouting', 'blooming', 'wilting', 'composting');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE garden_type AS ENUM ('wild', 'rows', 'greenhouse');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE fence_type AS ENUM ('public', 'friends', 'close_friends', 'orchard', 'private');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vine_growth AS ENUM ('seedling', 'vine', 'mature', 'ancient');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE nutrient_type AS ENUM ('nitrogen', 'toxin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Define enums for table creation (create_type=False since we created them above)
    seed_state_enum = postgresql.ENUM(
        'planted', 'sprouting', 'blooming', 'wilting', 'composting',
        name='seed_state',
        create_type=False
    )
    garden_type_enum = postgresql.ENUM(
        'wild', 'rows', 'greenhouse',
        name='garden_type',
        create_type=False
    )
    fence_type_enum = postgresql.ENUM(
        'public', 'friends', 'close_friends', 'orchard', 'private',
        name='fence_type',
        create_type=False
    )
    vine_growth_enum = postgresql.ENUM(
        'seedling', 'vine', 'mature', 'ancient',
        name='vine_growth',
        create_type=False
    )
    nutrient_type_enum = postgresql.ENUM(
        'nitrogen', 'toxin',
        name='nutrient_type',
        create_type=False
    )
    
    # Seeds table (posts/videos)
    op.create_table(
        'seeds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(512), nullable=True),
        sa.Column('thumbnail_url', sa.String(512), nullable=True),
        sa.Column('mux_asset_id', sa.String(255), nullable=True),
        sa.Column('mux_playback_id', sa.String(255), nullable=True),
        
        # Lifecycle state
        sa.Column('state', seed_state_enum, nullable=False, server_default='planted'),
        sa.Column('planted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('sprouts_at', sa.DateTime(), nullable=True),
        sa.Column('wilts_at', sa.DateTime(), nullable=True),
        sa.Column('composted_at', sa.DateTime(), nullable=True),
        
        # Growth metrics
        sa.Column('water_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('nutrient_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sunlight_hours', sa.Integer(), nullable=False, server_default='0'),
        
        # Garden location
        sa.Column('garden_type', garden_type_enum, nullable=False, server_default='wild'),
        sa.Column('privacy_fence', fence_type_enum, nullable=False, server_default='public'),
        
        # Soil data
        sa.Column('soil_health', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('pollination_vector', postgresql.ARRAY(sa.Float()), nullable=True),  # ML embedding
        
        # Soft delete
        sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'),
    )
    
    # Indexes for seeds
    op.create_index('idx_seeds_state', 'seeds', ['state'])
    op.create_index('idx_seeds_wilts_at', 'seeds', ['wilts_at'])
    op.create_index('idx_seeds_garden', 'seeds', ['garden_type', 'privacy_fence'])
    op.create_index('idx_seeds_vine', 'seeds', ['vine_id'])
    
    # Vines table (users with garden metrics)
    op.create_table(
        'vines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        
        # Vine health metrics
        sa.Column('root_strength', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('soil_health', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('growth_stage', vine_growth_enum, nullable=False, server_default='seedling'),
        
        # Activity tracking
        sa.Column('planted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_watered_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        
        # Growth paths (JSON array: ['personal', 'emotional'])
        sa.Column('selected_paths', postgresql.JSONB(), nullable=True),
        
        # Stats
        sa.Column('seeds_planted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('soil_given', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sunlight_received', sa.Integer(), nullable=False, server_default='0'),
    )
    
    op.create_index('idx_vines_soil_health', 'vines', ['soil_health'])
    op.create_index('idx_vines_user', 'vines', ['user_id'])
    
    # Soil table (comments as nutrients)
    op.create_table(
        'soil',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('seed_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seeds.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        
        # Nutrient value (net: nitrogen - toxins)
        sa.Column('nutrient_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('nitrogen_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('toxin_count', sa.Integer(), nullable=False, server_default='0'),
        
        # Lifecycle
        sa.Column('added_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('decays_at', sa.DateTime(), nullable=True),
        sa.Column('composted_at', sa.DateTime(), nullable=True),
        sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'),
    )
    
    op.create_index('idx_soil_seed', 'soil', ['seed_id'])
    op.create_index('idx_soil_decay', 'soil', ['seed_id', 'decays_at'])
    
    # Nutrients table (votes on comments)
    op.create_table(
        'nutrients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('soil_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('soil.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', nutrient_type_enum, nullable=False),
        sa.Column('strength', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('added_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_unique_constraint('uq_nutrient_vine_soil', 'nutrients', ['soil_id', 'vine_id'])
    op.create_index('idx_nutrients_soil', 'nutrients', ['soil_id'])
    
    # Fences table (privacy circles)
    op.create_table(
        'fences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fence_type', fence_type_enum, nullable=False),
        sa.Column('member_vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_unique_constraint('uq_fence_member', 'fences', ['vine_id', 'fence_type', 'member_vine_id'])
    op.create_index('idx_fences_vine', 'fences', ['vine_id'])
    
    # Roots table (direct messages)
    op.create_table(
        'roots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('from_vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('to_vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('decays_at', sa.DateTime(), nullable=True),
        sa.Column('composted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_roots_to_vine', 'roots', ['to_vine_id'])
    op.create_index('idx_roots_from_vine', 'roots', ['from_vine_id'])
    
    # Pollination events (discovery tracking)
    op.create_table(
        'pollination_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('seed_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seeds.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pathway', sa.String(50), nullable=False),  # 'wild_garden', 'rows', 'pollination'
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_pollination_seed', 'pollination_events', ['seed_id'])
    op.create_index('idx_pollination_vine', 'pollination_events', ['vine_id'])
    
    # Climate readings (community health snapshots)
    op.create_table(
        'climate_readings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('measured_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('toxicity_level', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('growth_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('drought_risk', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('pest_incidents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('temperature', sa.Float(), nullable=False, server_default='0.5'),
    )
    
    op.create_index('idx_climate_time', 'climate_readings', ['measured_at'])


def downgrade():
    # Drop tables
    op.drop_table('climate_readings')
    op.drop_table('pollination_events')
    op.drop_table('roots')
    op.drop_table('fences')
    op.drop_table('nutrients')
    op.drop_table('soil')
    op.drop_table('vines')
    op.drop_table('seeds')
    
    # Drop ENUMs
    op.execute('DROP TYPE nutrient_type')
    op.execute('DROP TYPE vine_growth')
    op.execute('DROP TYPE fence_type')
    op.execute('DROP TYPE garden_type')
    op.execute('DROP TYPE seed_state')
