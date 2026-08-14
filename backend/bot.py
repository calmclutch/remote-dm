import os
import asyncio
import threading

import discord
import uvicorn
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from backend.bot_server import app as bot_server_app
from backend.discord_service import set_bot
from database.database import (
    initialize_database,
    register_friend,
    get_registered_friends,
    add_alias,
    find_friend,
    is_registered,
    archive_and_unregister,
    save_message,
)


load_dotenv()


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("TEST_GUILD_ID")
OWNER_ID = os.getenv("OWNER_DISCORD_ID")


if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is not set in .env")

if not GUILD_ID:
    raise RuntimeError("TEST_GUILD_ID is not set in .env")

if not OWNER_ID:
    raise RuntimeError("OWNER_DISCORD_ID is not set in .env")


class RemoteDM(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.dm_messages = True
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):
        initialize_database()

        guild = discord.Object(id=int(GUILD_ID))

        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)

        print(f"Synced {len(synced)} slash commands to test server.")


bot = RemoteDM()


@bot.event
async def on_ready():
    set_bot(bot)
    print(f"Logged in as {bot.user}")


@bot.tree.command(
    name="ping",
    description="Check whether RemoteDM is online.",
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Pong! RemoteDM is alive.",
        ephemeral=True,
    )


class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(
        label="Allow",
        style=discord.ButtonStyle.success,
    )
    async def allow(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        register_friend(
            interaction.user.id,
            interaction.user.display_name,
        )

        await interaction.response.edit_message(
            content="✅ You're now registered with RemoteDM.",
            view=None,
        )

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.edit_message(
            content="Registration cancelled.",
            view=None,
        )


@bot.tree.command(
    name="register",
    description="Register with RemoteDM.",
)
async def register(interaction: discord.Interaction):
    if is_registered(interaction.user.id):
        await interaction.response.send_message(
            "You're already registered with RemoteDM.",
            ephemeral=True,
        )
        return

    view = RegisterView()

    await interaction.response.send_message(
        "RemoteDM can relay messages to and from you through Discord.\n\n"
        "Do you want to opt in?",
        view=view,
        ephemeral=True,
    )


@bot.tree.command(
    name="unregister",
    description="Opt out of RemoteDM.",
)
async def unregister(interaction: discord.Interaction):
    if not is_registered(interaction.user.id):
        await interaction.response.send_message(
            "You are not currently registered with RemoteDM.",
            ephemeral=True,
        )
        return

    archive_and_unregister(interaction.user.id)

    await interaction.response.send_message(
        "✅ You have been unregistered from RemoteDM.",
        ephemeral=True,
    )


@bot.tree.command(
    name="friends",
    description="Show people registered with RemoteDM.",
)
async def friends(interaction: discord.Interaction):
    if str(interaction.user.id) != OWNER_ID:
        await interaction.response.send_message(
            "You are not authorized to use this command.",
            ephemeral=True,
        )
        return

    friends = get_registered_friends()

    if not friends:
        await interaction.response.send_message(
            "No registered friends yet.",
            ephemeral=True,
        )
        return

    lines = []

    for friend in friends:
        lines.append(
            f"• {friend['display_name']} — `{friend['discord_user_id']}`"
        )

    await interaction.response.send_message(
        "\n".join(lines),
        ephemeral=True,
    )


@bot.tree.command(
    name="alias",
    description="Add an alias for your RemoteDM profile.",
)
@app_commands.describe(
    alias="The name people can use to refer to you."
)
async def alias(
    interaction: discord.Interaction,
    alias: str,
):
    success = add_alias(
        interaction.user.id,
        alias,
    )

    if not success:
        await interaction.response.send_message(
            "You need to register with /register first.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Alias `{alias}` added.",
        ephemeral=True,
    )


@bot.tree.command(
    name="find",
    description="Find a registered friend by name or alias.",
)
@app_commands.describe(
    name="Friend's name or alias"
)
async def find(
    interaction: discord.Interaction,
    name: str,
):
    if not is_registered(interaction.user.id):
        await interaction.response.send_message(
            "You need to register with /register first.",
            ephemeral=True,
        )
        return

    friend = find_friend(name)

    if friend is None:
        await interaction.response.send_message(
            "No registered friend found.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Found: {friend['display_name']} — `{friend['discord_user_id']}`",
        ephemeral=True,
    )


def start_internal_server():
    port = int(os.getenv("BOT_INTERNAL_PORT", "8765"))

    config = uvicorn.Config(
        bot_server_app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )

    server = uvicorn.Server(config)
    asyncio.run(server.serve())


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not isinstance(message.channel, discord.DMChannel):
        return

    if not is_registered(message.author.id):
        return

    save_message(
        sender_discord_user_id=message.author.id,
        recipient_discord_user_id=bot.user.id,
        direction="incoming",
        content=message.content,
    )

    print(
        f"Incoming DM from {message.author.display_name}: "
        f"{len(message.content)} characters"
    )

    await bot.process_commands(message)


threading.Thread(
    target=start_internal_server,
    daemon=True,
).start()


bot.run(TOKEN)