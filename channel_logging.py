# Imports
import os
import time
import discord
from discord.ext.commands import Bot, Cog, is_owner

import reference


# Class
class ChannelLogging(Cog):
    def __init__(self, client):
        self.client = client

    # Listener
    @Cog.listener()
    async def on_message(self, message):
        # Turn off logging if disabled in cpanel
        if self.client.channel_logging_enabled == False:
            return

        # The Robean General
        if message.channel.id == 696082479752413277: # Replace ID
            embed = discord.Embed(description=time.strftime('Sent at %I:%M %p on %b %d, %Y', time.localtime()), color=0x00ff00)
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)

            # Check if message has no content
            if not message.content:
                embed.add_field(name="TR - General", value="No Content")
            else:
                embed.add_field(name="TR - General", value=message.content)

            # Check if message has attachments
            if not not message.attachments:
                for i in message.attachments:
                    embed.add_field(name="Attachment", value=i.url)

            await self.client.theRobeanGeneral.send(embed=embed)


# Setup & Link
def setup(client):
    client.add_cog(ChannelLogging(client))
