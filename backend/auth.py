import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

API_SECRET = os.getenv("API_SECRET")

if not API_SECRET:
    raise RuntimeError("API_SECRET is not set in .env")

security = HTTPBearer()


def require_api_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    if credentials.credentials.strip() != API_SECRET.strip():
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return True