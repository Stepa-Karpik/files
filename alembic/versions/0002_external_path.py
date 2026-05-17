"""store external file paths"""
from alembic import op
import sqlalchemy as sa
revision="0002_external_path"; down_revision="0001_initial_files"; branch_labels=None; depends_on=None
def upgrade(): op.add_column("assets", sa.Column("external_path", sa.String(length=1024), nullable=True))
def downgrade(): op.drop_column("assets", "external_path")
