import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from backend.discord_service import send_dm

load_dotenv()

app = FastAPI()

BOT_INTERNAL_SECRET = os.getenv("BOT_INTERNAL_SECRET")

if not BOT_INTERNAL_SECRET:
    raise RuntimeError("BOT_INTERNAL_SECRET is not set in .env")


class DMRequest(BaseModel):
    discord_user_id: int
    message: str


@app.post("/internal/send-dm")
async def internal_send_dm(
    request: DMRequest,
    authorization: str | None = Header(default=None),
):
    if authorization != f"Bearer {BOT_INTERNAL_SECRET}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    try:
        await send_dm(
            request.discord_user_id,
            request.message,
        )
    except Exception as error:
        print(f"Discord DM error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send Discord message.",
        )

    return {"status": "sent"}