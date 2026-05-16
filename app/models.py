from datetime import UTC, datetime
from uuid import uuid4
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass
class AssetModel(Base):
    __tablename__ = 'assets'
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f'asset_{uuid4().hex}')
    storage_mode: Mapped[str] = mapped_column(String(32))
    owner_subject_id: Mapped[str] = mapped_column(String(128), index=True)
    filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    external_file_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    revision: Mapped[str | None] = mapped_column(String(255), nullable=True)
    path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
class LeaseModel(Base):
    __tablename__ = 'leases'
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f'lease_{uuid4().hex}')
    asset_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default='active')
class PreviewModel(Base):
    __tablename__ = 'previews'
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f'preview_{uuid4().hex}')
    asset_id: Mapped[str] = mapped_column(String(64), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    engine: Mapped[str] = mapped_column(String(64), default='onlyoffice')
    status: Mapped[str] = mapped_column(String(32), default='queued')
