from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base
from app.repositories import FileRepository


def test_asset_lease_and_preview_persist():
    engine = create_engine('sqlite+pysqlite:///:memory:')
    Base.metadata.create_all(engine)
    repo = FileRepository(Session(engine))
    asset = repo.create_external_asset(owner_subject_id='usr_1', provider='yandex_disk', external_file_id='disk_1', revision='rev_1')
    lease = repo.create_lease(asset_id=asset.id)
    preview = repo.create_preview(asset_id=asset.id, filename='contract.docx')
    assert repo.get_asset(asset.id).provider == 'yandex_disk'
    assert repo.close_lease(lease.id).status == 'closing'
    assert preview.engine == 'onlyoffice'
