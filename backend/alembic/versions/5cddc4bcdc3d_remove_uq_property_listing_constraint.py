"""remove uq_property_listing constraint

Revision ID: 5cddc4bcdc3d
Revises: 72e4215a6554
Create Date: 2026-10-23 00:07:06.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cddc4bcdc3d'
down_revision: Union[str, Sequence[str], None] = '72e4215a6554'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop uq_property_listing unique constraint to allow distinct properties."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'properties' in insp.get_table_names():
        constraints = [c['name'] for c in insp.get_unique_constraints('properties')]
        if 'uq_property_listing' in constraints:
            op.drop_constraint('uq_property_listing', 'properties', type_='unique')


def downgrade() -> None:
    """Recreate uq_property_listing unique constraint."""
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'properties' in insp.get_table_names():
        constraints = [c['name'] for c in insp.get_unique_constraints('properties')]
        if 'uq_property_listing' not in constraints:
            op.create_unique_constraint(
                'uq_property_listing',
                'properties',
                ['locality', 'sqft', 'bhk', 'rent']
            )
