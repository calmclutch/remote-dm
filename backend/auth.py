import os

from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

API_SECRET = os.getenv("API_SECRET")

if not API_SECRET:
    raise RuntimeError("API_SECRET is not set in .env")


def require_api_auth(
    authorization: str | None = Header(default=None),
):
    if authorization != f"Bearer {API_SECRET}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return True