# Imports
import os
import discord
import time
import sys
import random
import logging
import asyncio
import subprocess
from dotenv import load_dotenv
from discord.ext.commands import Bot
from datetime import datetime
from discord.ext.commands import CommandNotFound
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import discord_slash

import reference
import discordCommandOptions

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

# Initialize Discord client and slash command handler
client = Bot(command_prefix="?", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)

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
    print("Running version " + discord_slash.__version__ + " of Discord Interactions")
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
@slash.slash(name='restart', description="Discord bot restart command.", guild_ids=reference.guild_ids)
async def restart(context: SlashContext):
    if context.author.id == client.admin_id:
        await context.send(f"{client.checkmarkGlyph(context.guild)} Restart request accepted. Attempting to restart.")

        subprocess.Popen("sudo systemctl restart discord-bot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        await context.send(f"Restart request denied. {client.xmarkGlyph(context.guild)}")

# Shutdown Command
@slash.slash(name='shutdown', description="Discord bot shutdown command.", guild_ids=reference.guild_ids)
async def shutdown(context: SlashContext):
    if context.author.id == client.admin_id:
        await context.send(f"{client.checkmarkGlyph(context.guild)} Shutdown request accepted. Attempting to shutdown.")

        subprocess.Popen("sudo systemctl stop discord-bot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        await context.send(f"Shutdown request denied. {client.xmarkGlyph(context.guild)}")


# Ping Latency Test Command
@slash.slash(name='ping', description="Measure client-to-bot latency.", guild_ids=reference.guild_ids)
async def ping(context: SlashContext):
    beforeping = time.monotonic()
    messageping = await context.send("Pong!")
    pingtime = (time.monotonic() - beforeping) * 1000
    await messageping.edit(content=f"Pong! `{int(pingtime)}ms`")
    # print(f'Ping {int(pingtime)}ms @ ' + time.ctime())


# Load Cog Command
@slash.slash(name='load', description="Load cog manually.", options=discordCommandOptions.loadOpts, guild_ids=reference.guild_ids)
async def load(context: SlashContext, cog: str):
    if context.author.id == client.admin_id:
        try:
            client.load_extension(cog)
            msg = await context.send(f"Extension `{cog}` loaded. {client.checkmarkGlyph(context.guild)}")
        except Exception as e:
            msg = await context.send(f"{e} {client.xmarkGlyph(context.guild)}")
    else:
        msg = await context.send(f"Bot state change denied. {client.xmarkGlyph(context.guild)}")
    
    await asyncio.sleep(reference.cmd_msg_delete_cooldown)
    await msg.delete()


# # Load All Extensions
# @client.command(name='loadall')
# async def loadall(context):
#     if context.author.id == client.admin_id:
#         for extension in extensions:
#             try:
#                 client.load_extension(f"{extension}")
#             except Exception as e:
#                 await context.send(e)


# Unload Extension Manually
@slash.slash(name='unload', description="Unload cog manually.", options=discordCommandOptions.unloadOpts, guild_ids=reference.guild_ids)
async def unload(context: SlashContext, cog: str):
    if context.author.id == client.admin_id:
        try:
            client.unload_extension(cog)
            msg = await context.send(f"Extension `{cog}` unloaded. {client.checkmarkGlyph(context.guild)}")
        except Exception as e:
            msg = await context.send(f"{e} {client.xmarkGlyph(context.guild)}")
    else:
        msg = await context.send(f"Bot state change denied. {client.xmarkGlyph(context.guild)}")
    
    await asyncio.sleep(reference.cmd_msg_delete_cooldown)
    await msg.delete()


# # Unload All Extensions
# @client.command(name='unloadall')
# async def unloadall(context):
#     if context.author.id == client.admin_id:
#         for extension in extensions:
#             try:
#                 client.unload_extension(f"{extension}")
#             except Exception as e:
#                 await context.send(e)


# Reload Extensions
@slash.slash(name='reload', description="Reload cog.", options=discordCommandOptions.reloadOpts, guild_ids=reference.guild_ids)
async def unload(context: SlashContext, cog: str):
    if context.author.id == client.admin_id:
        client.unload_extension(cog)
        try:
            client.load_extension(cog)
            msg = await context.send(f"Extension `{cog}` reloaded. {client.checkmarkGlyph(context.guild)}")
        except Exception as e:
            msg = await context.send(f"{e} {client.xmarkGlyph(context.guild)}")
    else:
        msg = await context.send(f"Bot state change denied. {client.xmarkGlyph(context.guild)}")

    await asyncio.sleep(reference.cmd_msg_delete_cooldown)
    await msg.delete()

# # Custom Help
# @client.command(name='help')
# async def help(context):
#     await context.send(f"lol, who reads the manual? {context.author.mention}")

# Startup
if __name__ == "__main__":
    print()
    for cog in startup_cogs:
        try:
            print(f"Loading {cog}...", end=" ")
            client.load_extension(cog)
            print("Done!")
        except Exception as e:
            print(f"Failed to load {cog} with reason: {e}")
    print()

client.run(os.getenv('DISCORD_BOT_TOKEN'))
