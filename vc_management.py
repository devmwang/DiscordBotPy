import asyncio
import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference


class VCManagement(Cog):
    def __init__(self, client):
        self.client = client
           

    # Votekick From VC Command
    @app_commands.command(name='votekick')
    async def votekick(self, interaction: discord.Interaction, target: discord.Member):
        channel = interaction.author.voice.channel
        members = channel.members
        user_count = len(members)

        if interaction.author.voice:
            if target.id == self.client.admin_id:
                await interaction.guild.me.edit(nick="Dominion Voting Systems")

            embed = discord.Embed(title=f"Vote by: {interaction.author.display_name}", color=0xc6c6c6)
            embed.add_field(name="Kick player:", value=target.mention, inline=False)
            vote_message = await interaction.response.send_message(embed=embed)

            await vote_message.add_reaction(self.client.checkmarkGlyph(interaction.guild))
            await vote_message.add_reaction(self.client.xmarkGlyph(interaction.guild))

            check_reactions = 1
            reaction = 0
            while check_reactions < user_count:
                if check_reactions >= user_count:
                    break
                else:
                    try:
                        reaction = await self.client.wait_for(
                            'reaction_add', timeout=30.0, check=lambda reaction, user: reaction.emoji == self.client.checkmarkGlyph(interaction.guild)
                        )
                        if reaction != None:
                            check_reactions += 1
                        else:
                            break
                    except asyncio.TimeoutError:
                        embed_edit = discord.Embed(title="Vote Failed.", color=0xff0000)
                        embed_edit.add_field(name="Kick failed:", value="Not enough players voted.", inline=False)
                        await vote_message.clear_reactions()
                        await interaction.edit_original_response(embed=embed_edit)

            if check_reactions >= user_count:
                embed_edit = discord.Embed(title="Vote Passed!", color=0x00ff00)
                embed_edit.add_field(name="Kicking user...", value=target.mention, inline=False)
                await vote_message.clear_reactions()
                await interaction.edit_original_response(embed=embed_edit)

            if target.id == self.client.admin_id:
                await interaction.author.move_to(None)
                await interaction.guild.me.edit(nick="")

            else:
                await target.move_to(None)


# Setup & Link
async def setup(client):
    await client.add_cog(VCManagement(client))
