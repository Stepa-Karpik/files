from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app
from app.models import Base


def make_client():
    engine = create_engine('sqlite+pysqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)

    def override():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override
    return TestClient(app)


def test_managed_upload_stores_file_metadata():
    client = make_client()
    response = client.post('/api/v1/uploads/managed', data={'owner_subject_id': 'usr_1'}, files={'file': ('contract.pdf', b'pdf-bytes', 'application/pdf')})
    assert response.status_code == 201
    payload = response.json()
    assert payload['storage_mode'] == 'managed'
    assert payload['filename'] == 'contract.pdf'


def test_managed_uploads_with_same_filename_get_distinct_paths():
    client = make_client()
    first = client.post('/api/v1/uploads/managed', data={'owner_subject_id': 'usr_same'}, files={'file': ('same.pdf', b'one', 'application/pdf')})
    second = client.post('/api/v1/uploads/managed', data={'owner_subject_id': 'usr_same'}, files={'file': ('same.pdf', b'two', 'application/pdf')})
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()['filename'] == 'same.pdf'
    assert second.json()['filename'] == 'same.pdf'
    assert first.json()['path'] != second.json()['path']
