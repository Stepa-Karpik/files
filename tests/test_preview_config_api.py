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


def test_preview_editor_config_points_to_original_asset_url(monkeypatch):
    monkeypatch.setenv("FILES_PUBLIC_BASE_URL", "https://files.example")
    client = make_client()
    asset = client.post(
        "/api/v1/assets/managed",
        json={"owner_subject_id": "usr_1", "filename": "contract.docx", "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ).json()
    preview = client.post("/api/v1/previews", json={"asset_id": asset["asset_id"], "filename": "contract.docx"}).json()

    response = client.get(f"/api/v1/previews/{preview['preview_id']}/editor-config")

    assert response.status_code == 200
    assert response.json()["document"]["key"] == asset["asset_id"]
    assert response.json()["document"]["url"] == f"https://files.example/api/v1/assets/{asset['asset_id']}/content"
