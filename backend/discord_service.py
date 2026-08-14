import asyncio


_bot = None
_bot_loop = None


def set_bot(bot):
    global _bot
    global _bot_loop

    _bot = bot
    _bot_loop = asyncio.get_running_loop()


async def send_dm(discord_user_id: int, message: str):
    if _bot is None or _bot_loop is None:
        raise RuntimeError("Discord bot is not connected.")

    if asyncio.get_running_loop() is _bot_loop:
        user = await _bot.fetch_user(discord_user_id)
        await user.send(message)
        return

    future = asyncio.run_coroutine_threadsafe(
        _send_dm(discord_user_id, message),
        _bot_loop,
    )

    await asyncio.wrap_future(future)


async def _send_dm(discord_user_id: int, message: str):
    user = await _bot.fetch_user(discord_user_id)
    await user.send(message)