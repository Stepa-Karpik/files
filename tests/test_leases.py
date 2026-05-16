from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_temporary_original_lease_can_be_created_and_closed():
    asset = client.post('/api/v1/assets/external', json={'owner_subject_id': 'usr_1', 'provider': 'yandex_disk', 'external_file_id': 'disk_1', 'revision': 'rev_1'}).json()
    lease = client.post('/api/v1/leases', json={'asset_id': asset['asset_id']})
    assert lease.status_code == 201
    lease_id = lease.json()['lease_id']
    closed = client.post(f'/api/v1/leases/{lease_id}/close')
    assert closed.status_code == 200
    assert closed.json()['status'] == 'closing'
