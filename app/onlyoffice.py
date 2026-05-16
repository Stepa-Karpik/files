from pathlib import Path


def build_editor_config(*, file_id: str, filename: str, download_url: str) -> dict:
    return {
        'document': {
            'fileType': Path(filename).suffix.lstrip('.').lower(),
            'key': file_id,
            'title': filename,
            'url': download_url,
        },
        'editorConfig': {
            'mode': 'view',
        },
    }
