import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from backend.auth import require_api_auth
from backend.messaging import prepare_message

load_dotenv()

app = FastAPI(title="RemoteDM API")

BOT_INTERNAL_SECRET = os.getenv("BOT_INTERNAL_SECRET")
BOT_INTERNAL_PORT = os.getenv("BOT_INTERNAL_PORT", "8765")

if not BOT_INTERNAL_SECRET:
    raise RuntimeError("BOT_INTERNAL_SECRET is not set in .env")

class MessageRequest(BaseModel):
    recipient: str
    message: str


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


@app.post("/api/messages")
async def send_message(
    request: MessageRequest,
    _: bool = Depends(require_api_auth),
):
    try:
        prepared = prepare_message(
            request.recipient,
            request.message,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://127.0.0.1:{BOT_INTERNAL_PORT}/internal/send-dm",
                headers={
                    "Authorization": f"Bearer {BOT_INTERNAL_SECRET}",
                },
                json={
                    "discord_user_id": prepared["discord_user_id"],
                    "message": prepared["message"],
                },
                timeout=10.0,
            )

        response.raise_for_status()

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Discord messaging service unavailable.",
        )

    return {
        "status": "sent",
        "recipient": prepared["display_name"],
    }