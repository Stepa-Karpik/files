from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_managed_asset_can_be_registered():
    response = client.post('/api/v1/assets/managed', json={'owner_subject_id': 'usr_1', 'filename': 'contract.pdf', 'content_type': 'application/pdf'})
    assert response.status_code == 201
    assert response.json()['storage_mode'] == 'managed'
