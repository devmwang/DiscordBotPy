# Imports
import os
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

## Logging
# logger = logging.getLogger('discord')
# logger.setLevel(logging.INFO)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


# Initialize Env Variables
load_dotenv()

# Startup cogs
startup_cogs = ["jishaku", "exec", "cpanel", "bot_management", "on_message", "on_voice_state_update", "ftx", "channel_logging", "others", "vc_management", "clap"]

# Main Discord Guild
CONTROL_GUILD = discord.Object(id=746647021561053215)
MY_GUILD = discord.Object(id=696082479752413274)

# Initialize Discord client and slash command handler
intents = discord.Intents.default()
intents.message_content = True


# Extend default discord.Bot class to sync commands to guild
class MyClient(commands.Bot):
    def __init__(self, *, command_prefix, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
    
    async def setup_hook(self):
        # Copy global commands to guilds (Do not have to wait hour for global command updates to apply)
        self.tree.copy_global_to(guild=CONTROL_GUILD)
        await self.tree.sync(guild=CONTROL_GUILD)

        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


# Create client
client = MyClient(command_prefix="?", intents=intents)

# Admin User ID
client.admin_id = 315238599761330197

# Helper Methods
client.checkmarkGlyph = lambda guild : discord.utils.get(guild.emojis, name="checkmark")
client.xmarkGlyph = lambda guild : discord.utils.get(guild.emojis, name="xmark")





# On Ready
@client.event
async def on_ready():
    # Print Bot Information to Console
    print('Authenticated as')
    print("Username: " + client.user.name)
    print("User ID: " + str(client.user.id))

    print("""
--------------------------------------------------------------------------------------------------
 ____  _                       _     ____        _       _          ___        _ _              _
|  _ \(_)___  ___ ___  _ __ __| |   | __ )  ___ | |_    (_)___     / _ \ _ __ | (_)_ __   ___  | |
| | | | / __|/ __/ _ \| '__/ _` |   |  _ \ / _ \| __|   | / __|   | | | | '_ \| | | '_ \ / _ \ | |
| |_| | \__ \ (_| (_) | | | (_| |   | |_) | (_) | |_    | \__ \   | |_| | | | | | | | | |  __/ |_|
|____/|_|___/\___\___/|_|  \__,_|   |____/ \___/ \__|   |_|___/    \___/|_| |_|_|_|_| |_|\___| (_)
--------------------------------------------------------------------------------------------------
    """)

    print("Running version " + discord.__version__ + " of Discord.py")
    print('----------')
    print()


    # Set Logging Channels
    client.controlGuild = client.get_guild(reference.controlGuildId)
    client.logChannel = client.get_channel(reference.logChannelId)

    client.theRobeanGeneral = client.get_channel(reference.theRobeanGeneralChannelId)

    client.channel_logging_enabled = False

    # Startup Log
    embed = discord.Embed(title=f"Discord Bot is online!", color=0x00ff00)
    embed.add_field(name="Time: ", value=time.strftime('%I:%M:%S %p', time.localtime()))
    embed.add_field(name="Date: ", value=time.strftime('%B %d, %Y', time.localtime()))

    await client.logChannel.send(embed=embed)


# Restart Command
@client.tree.command(name='restart', description="Discord bot restart command.")
async def restart(interaction: discord.Interaction):
    if interaction.user.id == client.admin_id:
        await interaction.response.send_message(f"{client.checkmarkGlyph(interaction.guild)} Restart request accepted. Attempting to restart.")

        subprocess.Popen("sudo systemctl restart discord-bot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        await interaction.response.send_message(f"Restart request denied. {client.xmarkGlyph(interaction.guild)}")

# Shutdown Command
@client.tree.command(name='shutdown', description="Discord bot shutdown command.")
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == client.admin_id:
        await interaction.response.send_message(f"{client.checkmarkGlyph(interaction.guild)} Shutdown request accepted. Attempting to shutdown.")

        subprocess.Popen("sudo systemctl stop discord-bot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        await interaction.response.send_message(f"Shutdown request denied. {client.xmarkGlyph(interaction.guild)}")


# Ping Latency Test Command
@client.tree.command(name='ping', description="Measure client-to-bot latency.")
async def ping(interaction: discord.Interaction):
    before_ping = time.monotonic()
    await interaction.response.send_message("Pong!")
    ping_time = (time.monotonic() - before_ping) * 1000
    await interaction.edit_original_response(content=f"Pong! `{int(ping_time)}ms`")


# Load Cog Command
@client.tree.command(name='load', description="Load extension manually.")
@app_commands.describe(extension="Name of extension to load.")
async def load(interaction: discord.Interaction, extension: str):
    if interaction.user.id == client.admin_id:
        try:
            await client.load_extension(extension)
            msg = await interaction.response.send_message(f"Extension `{extension}` loaded. {client.checkmarkGlyph(interaction.guild)}")
        except Exception as e:
            msg = await interaction.response.send_message(f"{e} {client.xmarkGlyph(interaction.guild)}")
    else:
        msg = await interaction.response.send_message(f"Bot state change denied. {client.xmarkGlyph(interaction.guild)}")
    
    await asyncio.sleep(reference.cmd_msg_delete_cooldown)
    await msg.delete()


# Unload Extension Manually
@client.tree.command(name='unload', description="Unload extension manually.")
@app_commands.describe(extension="Name of extension to unload.")
async def unload(interaction: discord.Interaction, extension: str):
    if interaction.user.id == client.admin_id:
        try:
            await client.unload_extension(extension)
            msg = await interaction.response.send_message(f"Extension `{extension}` unloaded. {client.checkmarkGlyph(interaction.guild)}")
        except Exception as e:
            msg = await interaction.response.send_message(f"{e} {client.xmarkGlyph(interaction.guild)}")
    else:
        msg = await interaction.response.send_message(f"Bot state change denied. {client.xmarkGlyph(interaction.guild)}")
    
    await asyncio.sleep(reference.cmd_msg_delete_cooldown)
    await msg.delete()


# Reload Extensions
@client.tree.command(name='reload', description="Reload extension.")
@app_commands.describe(extension="Name of extension to reload.")
async def unload(interaction: discord.Interaction, extension: str):
    if interaction.user.id == client.admin_id:
        client.unload_extension(extension)
        try:
            client.load_extension(extension)
            msg = await interaction.response.send_message(f"Extension `{extension}` reloaded. {client.checkmarkGlyph(interaction.guild)}")
        except Exception as e:
            msg = await interaction.response.send_message(f"{e} {client.xmarkGlyph(interaction.guild)}")
    else:
        msg = await interaction.response.send_message(f"Bot state change denied. {client.xmarkGlyph(interaction.guild)}")

    await asyncio.sleep(reference.cmd_msg_delete_cooldown)
    await msg.delete()

# # Custom Help
# @client.command(name='help')
# async def help(context):
#     await interaction.response.send_message(f"lol, who reads the manual? {context.author.mention}")

# Startup
if __name__ == "__main__":
    print()
    # for cog in startup_cogs:
    #     try:
    #         print(f"Loading {cog}...", end=" ")
    #         client.load_extension(cog)
    #         print("Done!")
    #     except Exception as e:
    #         print(f"Failed to load {cog} with reason: {e}")
    print()

    client.run(os.getenv('DISCORD_BOT_TOKEN'))
