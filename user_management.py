# Imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands


# Class
class usermanagement(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Commands
        # Kick Command
        @client.command(name='serverkick')
        async def kick(context, user: discord.User, *, reason=None):
            checkmark = client.get_emoji(746648101443600414)
            xmark = client.get_emoji(746648138521116723)
            message = context.message
            if user.id == client.adminid:
                await guild.kick(user)
                await message.add_reaction(checkmark)
            else:
                await message.add_reaction(xmark)

        # Ban Command
        @client.command(name='serverban')
        async def ban(context, user: discord.User, *, reason=None):
            checkmark = client.get_emoji(746648101443600414)
            xmark = client.get_emoji(746648138521116723)
            message = context.message
            if user.id == client.adminid:
                await guild.ban(user)
                await message.add_reaction(checkmark)
            else:
                await message.add_reaction(xmark)


# Setup & Link
def setup(client):
    client.add_cog(usermanagement(client))
