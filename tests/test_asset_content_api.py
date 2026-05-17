from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app
from app.models import Base


def make_client():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)

    def override():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override
    return TestClient(app)


def test_managed_asset_content_returns_original_bytes(tmp_path, monkeypatch):
    client = make_client()
    target = tmp_path / "contract.pdf"
    target.write_bytes(b"pdf-bytes")
    monkeypatch.setattr("app.main.UPLOAD_DIR", tmp_path)
    uploaded = client.post(
        "/api/v1/uploads/managed",
        data={"owner_subject_id": "usr_1"},
        files={"file": ("contract.pdf", b"pdf-bytes", "application/pdf")},
    ).json()

    response = client.get(f"/api/v1/assets/{uploaded['asset_id']}/content")

    assert response.status_code == 200
    assert response.content == b"pdf-bytes"


def test_external_asset_content_is_materialized_on_demand(tmp_path, monkeypatch):
    client = make_client()
    monkeypatch.setattr("app.main.TEMP_DIR", tmp_path)

    class FakeIntegrationsClient:
        def download_external_content(self, **payload):
            assert payload["external_path"] == "disk:/Docs/invoice.pdf"
            return b"external-bytes"

    monkeypatch.setattr("app.main._build_integrations_client", lambda: FakeIntegrationsClient())
    asset = client.post(
        "/api/v1/assets/external",
        json={
            "owner_subject_id": "usr_1",
            "provider": "yandex_disk",
            "external_file_id": "disk_1",
            "external_path": "disk:/Docs/invoice.pdf",
            "revision": "rev_1",
            "filename": "invoice.pdf",
            "content_type": "application/pdf",
        },
    ).json()

    response = client.get(f"/api/v1/assets/{asset['asset_id']}/content")

    assert response.status_code == 200
    assert response.content == b"external-bytes"
