from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_external_file_registration_returns_asset():
    response = client.post('/api/v1/assets/external', json={'owner_subject_id': 'usr_1', 'provider': 'yandex_disk', 'external_file_id': 'disk_1', 'revision': 'rev_1'})
    assert response.status_code == 201
    assert response.json()['storage_mode'] == 'external'
