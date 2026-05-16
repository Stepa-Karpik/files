from uuid import uuid4
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="files")
assets: dict[str, dict] = {}
leases: dict[str, dict] = {}

class ExternalAssetCreate(BaseModel):
    owner_subject_id: str
    provider: str
    external_file_id: str
    revision: str

class LeaseCreate(BaseModel):
    asset_id: str

@app.get('/healthz')
def healthz(): return {'status': 'ok', 'service': 'files'}

@app.post('/api/v1/assets/external', status_code=status.HTTP_201_CREATED)
def register_external(payload: ExternalAssetCreate):
    asset_id = f'asset_{uuid4().hex}'
    asset = {'asset_id': asset_id, 'storage_mode': 'external', **payload.model_dump()}
    assets[asset_id] = asset
    return asset

@app.post('/api/v1/leases', status_code=status.HTTP_201_CREATED)
def create_lease(payload: LeaseCreate):
    lease_id = f'lease_{uuid4().hex}'
    lease = {'lease_id': lease_id, 'asset_id': payload.asset_id, 'status': 'active'}
    leases[lease_id] = lease
    return lease

@app.post('/api/v1/leases/{lease_id}/close')
def close_lease(lease_id: str):
    lease = leases[lease_id]
    lease['status'] = 'closing'
    return lease
