from app.onlyoffice import build_editor_config


def test_onlyoffice_config_preserves_original_document_identity():
    config = build_editor_config(file_id='asset_1', filename='contract.docx', download_url='https://files.example/download/asset_1')
    assert config['document']['fileType'] == 'docx'
    assert config['document']['url'].endswith('/asset_1')
    assert config['document']['key'] == 'asset_1'
