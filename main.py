# Imports
import os
import re
import time
import sys
import random
import logging
import asyncio
import subprocess
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands, tasks

import reference

# Initialize Env Variables
load_dotenv()

# Startup cogs
startup_cogs = [
    "jishaku",
    "exec",
    "cpanel",
    "bot_management",
    "on_message",
    "on_voice_state_update",
    "school",
    "ftx",
    "channel_logging",
    "others",
    "vc_management",
    "clap",
]

# Initialize Discord client and slash command handler
intents = discord.Intents.default()
intents.message_content = True


# Extend default discord.Bot class to sync commands to guild
class MyClient(commands.Bot):
    def __init__(self, *, command_prefix, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        # Copy global commands to guilds (Do not have to wait hour for global command updates to apply)
        self.tree.copy_global_to(guild=reference.CONTROL_GUILD)
        await self.tree.sync(guild=reference.CONTROL_GUILD)

        self.tree.copy_global_to(guild=reference.TR_GUILD)
        await self.tree.sync(guild=reference.TR_GUILD)

        self.tree.copy_global_to(guild=discord.Object(id=1049791344710787104))
        await self.tree.sync(guild=discord.Object(id=1049791344710787104))


def main():
    # Create client
    client = commands.Bot(command_prefix="?", intents=intents)

    # Initialize global state management system
    client.state = {}

    # Create subsystem states
    client.state["bot_management"] = {}

    # Admin User ID
    client.admin_id = 315238599761330197

    # Helper Methods
    client.checkmarkGlyph = lambda guild: discord.utils.get(
        guild.emojis, name="checkmark"
    )
    client.xmarkGlyph = lambda guild: discord.utils.get(guild.emojis, name="xmark")

    # On Ready
    @client.event
    async def on_ready():
        # Load Extensions
        print()
        for extension in reference.startup_extensions:
            try:
                print(f"Loading {extension}...", end=" ")
                await client.load_extension(extension)
                print("Done!")
            except Exception as e:
                print(f"Failed to load {extension} with reason: {e}")
        print()

        # Print Bot Information to Console
        print("Authenticated as")
        print("Username: " + client.user.name)
        print("User ID: " + str(client.user.id))

        print(
            """
    --------------------------------------------------------------------------------------------------
     ____  _                       _     ____        _       _          ___        _ _              _
    |  _ \(_)___  ___ ___  _ __ __| |   | __ )  ___ | |_    (_)___     / _ \ _ __ | (_)_ __   ___  | |
    | | | | / __|/ __/ _ \| "__/ _` |   |  _ \ / _ \| __|   | / __|   | | | | "_ \| | | "_ \ / _ \ | |
    | |_| | \__ \ (_| (_) | | | (_| |   | |_) | (_) | |_    | \__ \   | |_| | | | | | | | | |  __/ |_|
    |____/|_|___/\___\___/|_|  \__,_|   |____/ \___/ \__|   |_|___/    \___/|_| |_|_|_|_| |_|\___| (_)
    --------------------------------------------------------------------------------------------------
        """
        )

        print("Running version " + discord.__version__ + " of Discord.py")
        print("----------")
        print()

        client.tree.copy_global_to(guild=reference.CONTROL_GUILD)
        await client.tree.sync(guild=reference.CONTROL_GUILD)

        client.tree.copy_global_to(guild=reference.TR_GUILD)
        await client.tree.sync(guild=reference.TR_GUILD)

        client.tree.copy_global_to(guild=discord.Object(id=1049791344710787104))
        await client.tree.sync(guild=discord.Object(id=1049791344710787104))

        # Set Logging Channels
        client.controlGuild = client.get_guild(reference.CONTROL_GUILD_ID)
        client.logChannel = client.get_channel(reference.CONTROL_LOG_ID)

        client.theRobeanGeneral = client.get_channel(reference.TR_GUILD_GENERAL_ID)

        client.channel_logging_enabled = False

        # Startup Log
        embed = discord.Embed(title=f"Discord Bot is online!", color=0x00FF00)
        embed.add_field(
            name="Time: ", value=time.strftime("%I:%M:%S %p", time.localtime())
        )
        embed.add_field(
            name="Date: ", value=time.strftime("%B %d, %Y", time.localtime())
        )

        await client.logChannel.send(embed=embed)

    # Restart Command
    @client.tree.command(name="restart", description="Discord bot restart command.")
    async def restart(interaction: discord.Interaction):
        if interaction.user.id == client.admin_id:
            await interaction.response.send_message(
                f"{client.checkmarkGlyph(interaction.guild)} Restart request accepted. Attempting to restart."
            )

            subprocess.Popen(
                "sudo systemctl restart discord-bot",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            await interaction.response.send_message(
                f"Restart request denied. {client.xmarkGlyph(interaction.guild)}"
            )

    # Shutdown Command
    @client.tree.command(name="shutdown", description="Discord bot shutdown command.")
    async def shutdown(interaction: discord.Interaction):
        if interaction.user.id == client.admin_id:
            await interaction.response.send_message(
                f"{client.checkmarkGlyph(interaction.guild)} Shutdown request accepted. Attempting to shutdown."
            )

            subprocess.Popen(
                "sudo systemctl stop discord-bot",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            await interaction.response.send_message(
                f"Shutdown request denied. {client.xmarkGlyph(interaction.guild)}"
            )

    # Update Command
    @client.tree.command(name="update", description="Discord bot update command.")
    async def update(interaction: discord.Interaction):
        await interaction.response.defer()

        pipe = subprocess.Popen(
            "git pull", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = pipe.communicate()
        response = out.decode()
        error = err.decode()
        combined = response + error

        await interaction.followup.send(f"```{combined}```")

        if "Already up to date." in response:
            pass  # Do nothing
        elif "fatal" not in combined:
            updated_modules = set(re.findall(r"(\w+(?=\.py))", combined))

            await interaction.followup.send(
                "Successfully pulled updates from Github. Attempting to restart modified modules."
            )

            for module in updated_modules:
                try:
                    print(f"Reloading {module}...", end=" ")
                    await client.reload_extension(module)
                    print("Done!")
                except Exception as e:
                    print(f"Failed to reload {module} with reason: {e}")
                    await interaction.followup.send(
                        "Failed to reload 1 or more modules. Attempting to restart."
                    )
                    subprocess.Popen("sudo systemctl restart discord-bot", shell=True)
                    break
        else:
            await interaction.followup.send(
                "An error occurred, refer to system logs for more info."
            )

    # Ping Latency Test Command
    @client.tree.command(name="ping", description="Measure client-to-bot latency.")
    async def ping(interaction: discord.Interaction):
        before_ping = time.monotonic()
        await interaction.response.send_message("Pong!")
        ping_time = (time.monotonic() - before_ping) * 1000
        await interaction.edit_original_response(content=f"Pong! `{int(ping_time)}ms`")

    # # Custom Help
    # @client.command(name="help")
    # async def help(context):
    #     await interaction.response.send_message(f"lol, who reads the manual? {context.author.mention}")

    # Run Bot
    client.run(os.getenv("DISCORD_BOT_TOKEN"))


# Startup
if __name__ == "__main__":
    main()
