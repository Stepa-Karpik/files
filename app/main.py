from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, File, Form, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_session
from app.repositories import FileRepository

app=FastAPI(title='files')
UPLOAD_DIR=Path('storage/managed')
SessionDep=Annotated[Session,Depends(get_session)]
class ExternalAssetCreate(BaseModel): owner_subject_id:str; provider:str; external_file_id:str; revision:str
class ManagedAssetCreate(BaseModel): owner_subject_id:str; filename:str; content_type:str
class LeaseCreate(BaseModel): asset_id:str
class PreviewCreate(BaseModel): asset_id:str; filename:str
@app.get('/healthz')
def healthz(): return {'status':'ok','service':'files'}
@app.post('/api/v1/assets/external',status_code=status.HTTP_201_CREATED)
def register_external(payload:ExternalAssetCreate,session:SessionDep): return _asset(FileRepository(session).create_external_asset(**payload.model_dump()))
@app.post('/api/v1/assets/managed',status_code=status.HTTP_201_CREATED)
def register_managed(payload:ManagedAssetCreate,session:SessionDep): return _asset(FileRepository(session).create_managed_asset(**payload.model_dump()))
@app.post('/api/v1/leases',status_code=status.HTTP_201_CREATED)
def create_lease(payload:LeaseCreate,session:SessionDep): return _lease(FileRepository(session).create_lease(asset_id=payload.asset_id))
@app.post('/api/v1/leases/{lease_id}/close')
def close_lease(lease_id:str,session:SessionDep): return _lease(FileRepository(session).close_lease(lease_id))
@app.post('/api/v1/previews',status_code=status.HTTP_201_CREATED)
def create_preview(payload:PreviewCreate,session:SessionDep): return _preview(FileRepository(session).create_preview(**payload.model_dump()))
@app.post('/api/v1/uploads/managed',status_code=status.HTTP_201_CREATED)
async def upload_managed(session:SessionDep,owner_subject_id:str=Form(...),file:UploadFile=File(...)):
    UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
    target=UPLOAD_DIR/(file.filename or 'upload')
    target.write_bytes(await file.read())
    return _asset(FileRepository(session).create_managed_asset(owner_subject_id=owner_subject_id,filename=file.filename or target.name,content_type=file.content_type or 'application/octet-stream',path=str(target)))
def _asset(asset): return {'asset_id':asset.id,'storage_mode':asset.storage_mode,'owner_subject_id':asset.owner_subject_id,'filename':asset.filename,'content_type':asset.content_type,'provider':asset.provider,'external_file_id':asset.external_file_id,'revision':asset.revision,'path':asset.path}
def _lease(lease): return {'lease_id':lease.id,'asset_id':lease.asset_id,'status':lease.status}
def _preview(preview): return {'preview_id':preview.id,'asset_id':preview.asset_id,'filename':preview.filename,'engine':preview.engine,'status':preview.status}
