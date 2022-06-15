# Imports
import discord
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions


# Class
class Clap(Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    # Clap Command
    @cog_ext.cog_slash(name='clap', options=discordCommandOptions.clap, guild_ids=reference.guild_ids)
    async def clap(self, context: SlashContext, target, amount = 5):
        target = context.guild.get_member(int(target))

        if target.id == self.client.admin_id:
            await context.send(f"PTS is in effect. {self.client.xmarkGlyph(context.guild)}")
        else:
            for _ in range(0, int(amount)):
                await context.channel.send(f"Clapped {target.mention}")
            
            await context.send("Done!")

    # DM Clap Command
    @cog_ext.cog_slash(name='dmclap', options=discordCommandOptions.clap, guild_ids=reference.guild_ids)
    async def dmclap(self, context: SlashContext, target, amount = 5):
        target = context.guild.get_member(int(target))

        if target.id == self.client.admin_id:
            await context.send(f"PTS is in effect. {self.client.xmarkGlyph(context.guild)}")
        else:
            channel = await target.create_dm()
            for _ in range(0, amount):
                await channel.send(f"Clapped {target.mention}")
            
            await context.send("Done!")


# Setup & Link
def setup(client):
    client.add_cog(Clap(client))
