#Imports
import discord
from discord.ext.commands import Bot
from discord.ext import commands
##import youtube_dl

#Class
class music(commands.Cog):
    def __init__(self, client):
        self.client = client

        #Commands
        #Players Dictionary
##        players = {}
##
##        #Play Command
##        @client.command(name='play',aliases=['song'],
##                        pass_context=True)
##        async def play(context,*,url):
##            author = context.message.author
##            server = context.message.guild
##            channel = context.message.author.voice.voice_channel
##            await client.join_voice_channel(channel)
##            voice_client = client.voice_client_in(server)
##            player = await voice_client.create_ytdl(url)
##            players[service.id] = player
##            player.start()
##
##        #Leave Command
##        @client.command(name='leave',
##                        pass_context=True)
##        async def leave(context):
##            server = context.message.server
##            voice_client = client.voice_client_in(server)
##            await voice_client.disconnect()

#Setup & Link
def setup(client):
    client.add_cog(music(client))
