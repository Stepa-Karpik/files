from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


def build_editor_config(*, file_id: str, filename: str, download_url: str) -> dict:
    extension = Path(filename).suffix.lstrip('.').lower()
    config: dict[str, Any] = {
        'document': {
            'fileType': extension,
            'key': _document_key(file_id),
            'title': filename,
            'url': download_url,
            'permissions': {
                'download': True,
                'edit': False,
                'print': True,
            },
        },
        'documentType': _document_type(extension),
        'editorConfig': {
            'mode': 'view',
            'lang': 'ru',
        },
    }
    secret = os.getenv('ONLYOFFICE_JWT_SECRET') or os.getenv('JWT_SECRET') or 'change-me'
    if secret:
        config['token'] = _jwt_encode(config, secret)
    return config


def _document_key(file_id: str) -> str:
    return ''.join(ch if ch.isalnum() or ch in '._=-' else '_' for ch in file_id)[:128]


def _document_type(extension: str) -> str:
    if extension in {'xls', 'xlsx', 'ods', 'csv'}:
        return 'cell'
    if extension in {'ppt', 'pptx', 'odp'}:
        return 'slide'
    return 'word'


def _jwt_encode(payload: dict, secret: str) -> str:
    header = {'alg': 'HS256', 'typ': 'JWT'}
    signing_input = b'.'.join([
        _b64url(json.dumps(header, separators=(',', ':')).encode()),
        _b64url(json.dumps(payload, separators=(',', ':')).encode()),
    ])
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    return b'.'.join([signing_input, _b64url(signature)]).decode()


def _b64url(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b'=')
