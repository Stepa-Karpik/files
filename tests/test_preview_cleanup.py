from datetime import UTC, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import get_session
from app.main import app
from app.models import Base, LeaseModel


def make_client():
    engine = create_engine('sqlite+pysqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    def override_session():
        with factory() as session:
            yield session
    app.dependency_overrides[get_session] = override_session
    return TestClient(app), factory


def test_lease_heartbeat_and_cleanup_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.TEMP_DIR', tmp_path)
    client, factory = make_client()
    asset = client.post('/api/v1/assets/managed', json={'owner_subject_id':'usr_1','filename':'a.pdf','content_type':'application/pdf'}).json()
    temp = tmp_path/'a.pdf'; temp.write_text('x')
    with factory() as session:
        from app.repositories import FileRepository
        FileRepository(session).set_asset_path(asset['asset_id'], path=str(temp))
    lease = client.post('/api/v1/leases', json={'asset_id':asset['asset_id']}).json()
    assert client.post(f"/api/v1/leases/{lease['lease_id']}/heartbeat").json()['status'] == 'active'
    assert client.post(f"/api/v1/leases/{lease['lease_id']}/close").json()['status'] == 'closing'
    with factory() as session:
        row = session.get(LeaseModel, lease['lease_id'])
        row.close_after = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()
    result = client.post('/api/v1/leases/cleanup').json()
    assert result['deleted'] == 1
    assert not temp.exists()
