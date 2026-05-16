from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app
from app.models import Base


def make_client():
    engine=create_engine('sqlite+pysqlite:///:memory:',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory=sessionmaker(engine)
    def override():
        with factory() as session: yield session
    app.dependency_overrides[get_session]=override
    return TestClient(app)

def test_asset_survives_across_requests():
    client=make_client()
    asset=client.post('/api/v1/assets/managed',json={'owner_subject_id':'usr_1','filename':'contract.pdf','content_type':'application/pdf'}).json()
    lease=client.post('/api/v1/leases',json={'asset_id':asset['asset_id']})
    assert lease.status_code==201
