import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference


class Clap(Cog):
    def __init__(self, client: Bot):
        self.client = client

    # Commands
    # Clap Command
    @app_commands.command(name='clap', description='Clap!')
    @app_commands.describe(target="Target to clap.", amount="Times to clap user.")
    async def clap(self, interaction: discord.Interaction, target: discord.Member, amount: int = 5):
        if target.id == self.client.admin_id:
            await interaction.response.send_message(f"PTS is in effect. {self.client.xmarkGlyph(interaction.guild)}")
        else:
            await interaction.response.send_message(content=f"Initiating clapping.")

            for _ in range(0, int(amount)):
                await interaction.channel.send(f"Clapped {target.mention}")

            await interaction.followup.send(content="Done!")

    # DM Clap Command
    @app_commands.command(name='dmclap')
    @app_commands.describe(target="Target to clap.", amount="Times to clap user.")
    async def dmclap(self, interaction: discord.Interaction, target: discord.Member, amount: int = 5):
        # if target.id == self.client.admin_id:
        #     await interaction.response.send_message(f"PTS is in effect. {self.client.xmarkGlyph(interaction.guild)}")
        # else:
        await interaction.response.send_message(content=f"Initiating clapping.")

        for _ in range(0, amount):
            await target.send(f"Clapped {target.mention}")
        
        await interaction.followup.send(content="Done!")


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(Clap(client))
