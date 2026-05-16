from fastapi import FastAPI

app = FastAPI(title="files")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "files"}
