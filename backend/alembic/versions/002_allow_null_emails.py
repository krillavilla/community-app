"""Allow null emails for client credentials auth

Revision ID: 002_allow_null_emails
Revises: 001_video_gdpr
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_allow_null_emails'
down_revision = '001_video_gdpr'
branch_labels = None
depends_on = None


def upgrade():
    # TODO: Allow email to be null for machine-to-machine (client credentials) authentication
    op.alter_column('users', 'email',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade():
    # Note: This will fail if there are null emails in the database
    op.alter_column('users', 'email',
                    existing_type=sa.String(255),
                    nullable=False)
