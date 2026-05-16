from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_managed_upload_stores_file_metadata():
    response = client.post('/api/v1/uploads/managed', data={'owner_subject_id': 'usr_1'}, files={'file': ('contract.pdf', b'pdf-bytes', 'application/pdf')})
    assert response.status_code == 201
    payload = response.json()
    assert payload['storage_mode'] == 'managed'
    assert payload['filename'] == 'contract.pdf'
