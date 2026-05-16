from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_preview_session_can_be_created_for_asset():
    asset = client.post('/api/v1/assets/external', json={'owner_subject_id': 'usr_1', 'provider': 'yandex_disk', 'external_file_id': 'disk_1', 'revision': 'rev_1'}).json()
    preview = client.post('/api/v1/previews', json={'asset_id': asset['asset_id'], 'filename': 'contract.docx'})
    assert preview.status_code == 201
    assert preview.json()['status'] == 'queued'
    assert preview.json()['engine'] == 'onlyoffice'
