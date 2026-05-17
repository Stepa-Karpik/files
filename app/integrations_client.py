import httpx


class HttpIntegrationsClient:
    def __init__(self, *, base_url: str, transport: httpx.BaseTransport | None = None):
        self.base_url = base_url
        self.transport = transport

    def download_external_content(self, *, owner_subject_id: str, provider: str, external_path: str) -> bytes:
        with httpx.Client(base_url=self.base_url, transport=self.transport) as client:
            response = client.get(
                "/api/v1/external-files/content",
                params={
                    "owner_subject_id": owner_subject_id,
                    "provider": provider,
                    "external_path": external_path,
                },
            )
            response.raise_for_status()
            return response.content
