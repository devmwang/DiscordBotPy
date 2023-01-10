import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference


# Class
class School(Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    # Show Timetable Command
    @app_commands.command(name="timetable", description="Produce class timetable.")
    async def clap(self, interaction: discord.Interaction):

        await interaction.response.send_message(
            content=f"https://files.devmwang.com/wAba9/PedAVuGE23.png"
        )


# Setup & Link
async def setup(client):
    await client.add_cog(School(client))
