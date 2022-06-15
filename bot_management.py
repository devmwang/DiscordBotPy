# Imports
import asyncio
import json
import subprocess
import time
import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, is_owner
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions

# Class
class BotManagement(Cog):
    def __init__(self, client):
        self.client = client

    # * Commands
    # Crypto Price Bot Restart Command
    @cog_ext.cog_slash(name="restartpricebots", guild_ids=reference.guild_ids)
    async def restartpricebots(self, context: SlashContext):
        try:
            pipe = subprocess.Popen("sudo systemctl restart crypto-price-bots", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = pipe.communicate()
            error = err.decode()
            response = out.decode()
            combined = response + error
            if combined == "":
                msg = await context.send(f"{self.client.checkmarkGlyph(context.guild)} Crypto price bots restarted successfully.")
                await asyncio.sleep(5)
                await msg.delete()
            else:
                await context.send(f"```{combined}```")
        except discord.errors.HTTPException as _e:
            await context.send(self.client.xmarkGlyph(context.guild), _e)


# Setup & Link
def setup(client):
    client.add_cog(BotManagement(client))
