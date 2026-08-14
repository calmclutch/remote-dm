import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from backend.auth import require_api_auth
from backend.messaging import prepare_message
from database.database import (
    get_conversation,
    get_messages,
    save_message,
)


load_dotenv()


app = FastAPI(title="RemoteDM API")


BOT_INTERNAL_SECRET = os.getenv("BOT_INTERNAL_SECRET")
BOT_INTERNAL_PORT = os.getenv("BOT_INTERNAL_PORT", "8765")
OWNER_DISCORD_ID = os.getenv("OWNER_DISCORD_ID")


if not BOT_INTERNAL_SECRET:
    raise RuntimeError("BOT_INTERNAL_SECRET is not set in .env")

if not OWNER_DISCORD_ID:
    raise RuntimeError("OWNER_DISCORD_ID is not set in .env")


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

@app.get("/api/conversations/{discord_user_id}")
async def get_conversation_messages(
    discord_user_id: int,
    _: bool = Depends(require_api_auth),
):
    messages = get_conversation(discord_user_id)

    return {
        "recipient_id": discord_user_id,
        "messages": [
            {
                "id": message["id"],
                "sender_discord_user_id": message["sender_discord_user_id"],
                "recipient_discord_user_id": message["recipient_discord_user_id"],
                "direction": message["direction"],
                "content": message["content"],
                "created_at": message["created_at"],
            }
            for message in messages
        ],
    }

@app.get("/api/messages/{discord_user_id}")
async def get_user_messages(
    discord_user_id: int,
    _: bool = Depends(require_api_auth),
):
    messages = get_messages(discord_user_id)

    return {
        "messages": [
            {
                "id": message["id"],
                "sender_discord_user_id": message["sender_discord_user_id"],
                "recipient_discord_user_id": message["recipient_discord_user_id"],
                "direction": message["direction"],
                "content": message["content"],
                "created_at": message["created_at"],
            }
            for message in messages
        ]
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

    save_message(
        sender_discord_user_id=int(OWNER_DISCORD_ID),
        recipient_discord_user_id=prepared["discord_user_id"],
        direction="outgoing",
        content=prepared["message"],
    )

    return {
        "status": "sent",
        "recipient": prepared["display_name"],
    }