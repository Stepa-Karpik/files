from datetime import UTC, datetime, timedelta
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import AssetModel, LeaseModel, PreviewModel

class FileRepository:
    def __init__(self, session: Session): self.session = session
    def create_external_asset(self, **payload) -> AssetModel:
        asset = AssetModel(storage_mode='external', **payload); self.session.add(asset); self.session.commit(); self.session.refresh(asset); return asset
    def create_managed_asset(self, **payload) -> AssetModel:
        asset = AssetModel(storage_mode='managed', **payload); self.session.add(asset); self.session.commit(); self.session.refresh(asset); return asset
    def get_asset(self, asset_id: str) -> AssetModel | None: return self.session.get(AssetModel, asset_id)
    def set_asset_path(self, asset_id: str, *, path: str) -> AssetModel:
        asset=self.get_asset(asset_id); assert asset is not None; asset.path=path; self.session.commit(); self.session.refresh(asset); return asset
    def create_lease(self, *, asset_id: str) -> LeaseModel:
        lease = LeaseModel(asset_id=asset_id); self.session.add(lease); self.session.commit(); self.session.refresh(lease); return lease
    def close_lease(self, lease_id: str) -> LeaseModel:
        lease = self.session.get(LeaseModel, lease_id); assert lease is not None; lease.status='closing'; lease.close_after=datetime.now(UTC)+timedelta(seconds=30); self.session.commit(); self.session.refresh(lease); return lease
    def heartbeat_lease(self, lease_id: str) -> LeaseModel:
        lease = self.session.get(LeaseModel, lease_id); assert lease is not None; lease.status='active'; lease.last_heartbeat_at=datetime.now(UTC); lease.close_after=None; self.session.commit(); self.session.refresh(lease); return lease
    def cleanup_leases(self, *, heartbeat_timeout_seconds: int = 120) -> int:
        now = datetime.now(UTC)
        leases = list(self.session.scalars(select(LeaseModel).where(LeaseModel.status != 'deleted')).all())
        deleted = 0
        for lease in leases:
            heartbeat_at = _as_utc(lease.last_heartbeat_at)
            if lease.status == 'active' and heartbeat_at and heartbeat_at < now - timedelta(seconds=heartbeat_timeout_seconds):
                lease.status = 'expired'
                lease.close_after = now
            close_after = _as_utc(lease.close_after)
            if close_after and close_after <= now:
                asset = self.get_asset(lease.asset_id)
                if asset and asset.path:
                    path = Path(asset.path)
                    try:
                        is_temp = path.resolve().is_relative_to(Path('storage/temp').resolve())
                    except Exception:
                        is_temp = False
                    try:
                        is_managed_original = path.resolve().is_relative_to(Path('storage/managed').resolve())
                    except Exception:
                        is_managed_original = False
                    if asset.storage_mode == 'external' or is_temp or not is_managed_original:
                        if path.exists():
                            path.unlink()
                        if asset.storage_mode == 'external':
                            asset.path = None
                lease.status = 'deleted'
                lease.deleted_at = now
                deleted += 1
        self.session.commit()
        return deleted
    def create_preview(self, *, asset_id: str, filename: str) -> PreviewModel:
        lease = self.create_lease(asset_id=asset_id)
        preview = PreviewModel(asset_id=asset_id, filename=filename, lease_id=lease.id); self.session.add(preview); self.session.commit(); self.session.refresh(preview); return preview
    def get_preview(self, preview_id: str) -> PreviewModel | None: return self.session.get(PreviewModel, preview_id)

def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
