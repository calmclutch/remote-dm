import os

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from database.database import (
    initialize_database,
    register_friend,
    get_registered_friends,
    add_alias,
    find_friend,
    is_registered,
    archive_and_unregister,
)
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
    description="Register with RemoteDM."
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
    description="Opt out of RemoteDM."
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
    description="Show people registered with RemoteDM."
)
async def friends(interaction: discord.Interaction):
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
    description="Add an alias for your RemoteDM profile."
)
@app_commands.describe(alias="The name people can use to refer to you.")
async def alias(interaction: discord.Interaction, alias: str):
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
    description="Find a registered friend by name or alias."
)
@app_commands.describe(name="Friend's name or alias")
async def find(interaction: discord.Interaction, name: str):
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
bot.run(TOKEN)