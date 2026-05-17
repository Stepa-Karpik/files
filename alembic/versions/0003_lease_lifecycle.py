from alembic import op
import sqlalchemy as sa
revision = '0003_lease_lifecycle'
down_revision = '0002_external_path'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('leases', sa.Column('last_heartbeat_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('leases', sa.Column('close_after', sa.DateTime(timezone=True), nullable=True))
    op.add_column('leases', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('previews', sa.Column('lease_id', sa.String(length=64), nullable=True))

def downgrade():
    op.drop_column('previews', 'lease_id')
    op.drop_column('leases', 'deleted_at')
    op.drop_column('leases', 'close_after')
    op.drop_column('leases', 'last_heartbeat_at')
