# Imports
import discord
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions


# Class
class School(Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    # Clap Command


# Setup & Link
def setup(client):
    client.add_cog(School(client))
