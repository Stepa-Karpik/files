import os
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_session
from app.repositories import FileRepository
from app.onlyoffice import build_editor_config
from app.integrations_client import HttpIntegrationsClient

app=FastAPI(title='files')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in os.getenv('FRONTEND_ORIGINS', 'http://localhost:3200').split(',') if origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
UPLOAD_DIR=Path('storage/managed')
TEMP_DIR=Path('storage/temp')
SessionDep=Annotated[Session,Depends(get_session)]
class ExternalAssetCreate(BaseModel): owner_subject_id:str; provider:str; external_file_id:str; revision:str; external_path:str|None=None; filename:str|None=None; content_type:str|None=None
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
@app.get('/api/v1/previews/{preview_id}/editor-config')
def get_preview_editor_config(preview_id:str,session:SessionDep):
    preview=FileRepository(session).get_preview(preview_id)
    if preview is None: raise HTTPException(status_code=404,detail='preview not found')
    public_base=os.getenv('FILES_PUBLIC_BASE_URL','http://localhost:8320').rstrip('/')
    return build_editor_config(file_id=preview.asset_id,filename=preview.filename,download_url=f'{public_base}/api/v1/assets/{preview.asset_id}/content')
@app.get('/api/v1/assets/{asset_id}/content')
def get_asset_content(asset_id:str,session:SessionDep):
    asset=FileRepository(session).get_asset(asset_id)
    if asset is None: raise HTTPException(status_code=404,detail='asset content not available')
    if asset.path is None and asset.storage_mode == 'external':
        if asset.external_path is None: raise HTTPException(status_code=404,detail='asset content not available')
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        target=TEMP_DIR/f"{asset.id}-{asset.filename or 'external'}"
        target.write_bytes(_build_integrations_client().download_external_content(
            owner_subject_id=asset.owner_subject_id,
            provider=asset.provider or '',
            external_path=asset.external_path,
        ))
        asset=FileRepository(session).set_asset_path(asset.id, path=str(target))
    if asset.path is None: raise HTTPException(status_code=404,detail='asset content not available')
    return FileResponse(asset.path,media_type=asset.content_type or 'application/octet-stream',filename=asset.filename)
@app.post('/api/v1/uploads/managed',status_code=status.HTTP_201_CREATED)
async def upload_managed(session:SessionDep,owner_subject_id:str=Form(...),file:UploadFile=File(...)):
    UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
    target=UPLOAD_DIR/(file.filename or 'upload')
    target.write_bytes(await file.read())
    return _asset(FileRepository(session).create_managed_asset(owner_subject_id=owner_subject_id,filename=file.filename or target.name,content_type=file.content_type or 'application/octet-stream',path=str(target)))
def _asset(asset): return {'asset_id':asset.id,'storage_mode':asset.storage_mode,'owner_subject_id':asset.owner_subject_id,'filename':asset.filename,'content_type':asset.content_type,'provider':asset.provider,'external_file_id':asset.external_file_id,'revision':asset.revision,'path':asset.path}
def _build_integrations_client() -> HttpIntegrationsClient:
    return HttpIntegrationsClient(base_url=os.getenv('INTEGRATIONS_BASE_URL', 'http://integrations:8310'))
def _lease(lease): return {'lease_id':lease.id,'asset_id':lease.asset_id,'status':lease.status}
def _preview(preview): return {'preview_id':preview.id,'asset_id':preview.asset_id,'filename':preview.filename,'engine':preview.engine,'status':preview.status}
