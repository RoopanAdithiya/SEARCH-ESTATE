"""create properties table

Revision ID: 72e4215a6554
Revises: 
Create Date: 2026-10-22 22:57:56.875079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72e4215a6554'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely and idempotently."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = insp.get_table_names()

    if 'properties' not in tables:
        op.create_table(
            'properties',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('locality', sa.String(), nullable=True),
            sa.Column('sqft', sa.Integer(), nullable=True),
            sa.Column('bhk', sa.Integer(), nullable=True),
            sa.Column('furnishing', sa.String(), nullable=True),
            sa.Column('water_source', sa.String(), nullable=True),
            sa.Column('age', sa.Integer(), nullable=True),
            sa.Column('rent', sa.Integer(), nullable=True),
            sa.Column('bachelor_friendly', sa.Boolean(), nullable=True),
            sa.Column('pet_friendly', sa.Boolean(), nullable=True),
            sa.Column('lat', sa.Float(), nullable=True),
            sa.Column('lng', sa.Float(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('locality', 'sqft', 'bhk', 'rent', name='uq_property_listing')
        )
        op.create_index(op.f('ix_properties_id'), 'properties', ['id'], unique=False)
    else:
        # Table exists (e.g. existing local database), ensure constraint exists
        existing_constraints = [c['name'] for c in insp.get_unique_constraints('properties')]
        if 'uq_property_listing' not in existing_constraints:
            try:
                op.create_unique_constraint(
                    'uq_property_listing',
                    'properties',
                    ['locality', 'sqft', 'bhk', 'rent']
                )
            except Exception as e:
                print(f"Warning: Could not create uq_property_listing (may contain duplicates): {e}")


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = insp.get_table_names()
    if 'properties' in tables:
        op.drop_index(op.f('ix_properties_id'), table_name='properties')
        op.drop_table('properties')
