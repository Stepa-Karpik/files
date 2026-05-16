"""initial files schema"""
from alembic import op
import sqlalchemy as sa
revision='0001_initial_files'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('assets',sa.Column('id',sa.String(64),primary_key=True),sa.Column('storage_mode',sa.String(32),nullable=False),sa.Column('owner_subject_id',sa.String(128),nullable=False),sa.Column('filename',sa.String(512)),sa.Column('content_type',sa.String(255)),sa.Column('provider',sa.String(64)),sa.Column('external_file_id',sa.String(512)),sa.Column('revision',sa.String(255)),sa.Column('path',sa.String(1024)),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False)); op.create_index('ix_assets_owner_subject_id','assets',['owner_subject_id'])
    op.create_table('leases',sa.Column('id',sa.String(64),primary_key=True),sa.Column('asset_id',sa.String(64),nullable=False),sa.Column('status',sa.String(32),nullable=False)); op.create_index('ix_leases_asset_id','leases',['asset_id'])
    op.create_table('previews',sa.Column('id',sa.String(64),primary_key=True),sa.Column('asset_id',sa.String(64),nullable=False),sa.Column('filename',sa.String(512),nullable=False),sa.Column('engine',sa.String(64),nullable=False),sa.Column('status',sa.String(32),nullable=False)); op.create_index('ix_previews_asset_id','previews',['asset_id'])
def downgrade():
    op.drop_index('ix_previews_asset_id',table_name='previews'); op.drop_table('previews'); op.drop_index('ix_leases_asset_id',table_name='leases'); op.drop_table('leases'); op.drop_index('ix_assets_owner_subject_id',table_name='assets'); op.drop_table('assets')
