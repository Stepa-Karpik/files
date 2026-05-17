from sqlalchemy.orm import Session
from app.models import AssetModel, LeaseModel, PreviewModel

class FileRepository:
    def __init__(self, session: Session): self.session = session
    def create_external_asset(self, **payload) -> AssetModel:
        asset = AssetModel(storage_mode='external', **payload); self.session.add(asset); self.session.commit(); self.session.refresh(asset); return asset
    def create_managed_asset(self, **payload) -> AssetModel:
        asset = AssetModel(storage_mode='managed', **payload); self.session.add(asset); self.session.commit(); self.session.refresh(asset); return asset
    def get_asset(self, asset_id: str) -> AssetModel | None: return self.session.get(AssetModel, asset_id)
    def create_lease(self, *, asset_id: str) -> LeaseModel:
        lease = LeaseModel(asset_id=asset_id); self.session.add(lease); self.session.commit(); self.session.refresh(lease); return lease
    def close_lease(self, lease_id: str) -> LeaseModel:
        lease = self.session.get(LeaseModel, lease_id); assert lease is not None; lease.status='closing'; self.session.commit(); self.session.refresh(lease); return lease
    def create_preview(self, *, asset_id: str, filename: str) -> PreviewModel:
        preview = PreviewModel(asset_id=asset_id, filename=filename); self.session.add(preview); self.session.commit(); self.session.refresh(preview); return preview
    def get_preview(self, preview_id: str) -> PreviewModel | None: return self.session.get(PreviewModel, preview_id)
