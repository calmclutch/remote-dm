from fastapi import Depends, FastAPI

from backend.auth import require_api_auth


app = FastAPI(title="RemoteDM API")


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "RemoteDM",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


@app.get("/api/test")
async def protected_test(
    _: bool = Depends(require_api_auth),
):
    return {
        "authenticated": True,
    }