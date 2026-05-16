from uuid import uuid4
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="files")
class ExternalAssetCreate(BaseModel):
    owner_subject_id: str
    provider: str
    external_file_id: str
    revision: str
@app.get('/healthz')
def healthz(): return {'status': 'ok', 'service': 'files'}
@app.post('/api/v1/assets/external', status_code=status.HTTP_201_CREATED)
def register_external(payload: ExternalAssetCreate):
    return {'asset_id': f'asset_{uuid4().hex}', 'storage_mode': 'external', **payload.model_dump()}
