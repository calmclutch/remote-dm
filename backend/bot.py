import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database.database import initialize_database, register_friend

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("TEST_GUILD_ID")

if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is not set in .env")

if not GUILD_ID:
    raise RuntimeError("TEST_GUILD_ID is not set in .env")


class RemoteDM(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()

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
    print(f"Logged in as {bot.user}")


@bot.tree.command(
    name="ping",
    description="Check whether RemoteDM is online."
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Pong! RemoteDM is alive.",
        ephemeral=True,
    )


@bot.tree.command(
    name="register",
    description="Opt in to receiving messages from RemoteDM."
)
async def register(interaction: discord.Interaction):
    register_friend(
        interaction.user.id,
        interaction.user.display_name,
    )

    await interaction.response.send_message(
        "You're registered with RemoteDM.",
        ephemeral=True,
    )


bot.run(TOKEN)