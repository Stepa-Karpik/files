from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, status
from pydantic import BaseModel

app = FastAPI(title="files")
assets: dict[str, dict] = {}
leases: dict[str, dict] = {}
previews: dict[str, dict] = {}
UPLOAD_DIR = Path("storage/managed")

class ExternalAssetCreate(BaseModel):
    owner_subject_id: str
    provider: str
    external_file_id: str
    revision: str

class ManagedAssetCreate(BaseModel):
    owner_subject_id: str
    filename: str
    content_type: str

class LeaseCreate(BaseModel):
    asset_id: str

class PreviewCreate(BaseModel):
    asset_id: str
    filename: str

@app.get('/healthz')
def healthz(): return {'status': 'ok', 'service': 'files'}

@app.post('/api/v1/assets/external', status_code=status.HTTP_201_CREATED)
def register_external(payload: ExternalAssetCreate):
    asset_id = f'asset_{uuid4().hex}'
    asset = {'asset_id': asset_id, 'storage_mode': 'external', **payload.model_dump()}
    assets[asset_id] = asset
    return asset

@app.post('/api/v1/assets/managed', status_code=status.HTTP_201_CREATED)
def register_managed(payload: ManagedAssetCreate):
    asset_id = f'asset_{uuid4().hex}'
    asset = {'asset_id': asset_id, 'storage_mode': 'managed', **payload.model_dump()}
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

@app.post('/api/v1/previews', status_code=status.HTTP_201_CREATED)
def create_preview(payload: PreviewCreate):
    preview_id = f'preview_{uuid4().hex}'
    preview = {'preview_id': preview_id, 'asset_id': payload.asset_id, 'filename': payload.filename, 'engine': 'onlyoffice', 'status': 'queued'}
    previews[preview_id] = preview
    return preview


@app.post('/api/v1/uploads/managed', status_code=status.HTTP_201_CREATED)
async def upload_managed(owner_subject_id: str = Form(...), file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    asset_id = f'asset_{uuid4().hex}'
    target = UPLOAD_DIR / asset_id
    target.write_bytes(await file.read())
    asset = {
        'asset_id': asset_id,
        'storage_mode': 'managed',
        'owner_subject_id': owner_subject_id,
        'filename': file.filename or asset_id,
        'content_type': file.content_type or 'application/octet-stream',
        'path': str(target),
    }
    assets[asset_id] = asset
    return asset
