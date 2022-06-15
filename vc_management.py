# Imports
import asyncio
import discord
from discord import guild
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions


# Class
class VCManagement(Cog):
    def __init__(self, client):
        self.client = client
           

    # Votekick From VC Command
    @cog_ext.cog_slash(name='votekick', options=discordCommandOptions.votekick, guild_ids=reference.guild_ids)
    async def votekick(self, context: SlashContext, target):
        target = context.guild.get_member(int(target))
        channel = context.author.voice.channel
        members = channel.members
        usercount = len(members)

        if context.author.voice:
            # If target is admin, kick vote caller
            if target.id == self.client.admin_id:
                await context.guild.me.edit(nick="Dominion Voting Systems")

                embed = discord.Embed(title=f"Vote by: {context.author.display_name}", color=0xc6c6c6)
                embed.add_field(name="Kick player:", value=target.mention, inline=False)
                votemessage = await context.send(embed=embed)

                await votemessage.add_reaction(self.client.checkmarkGlyph(context.guild))
                await votemessage.add_reaction(self.client.xmarkGlyph(context.guild))

                check_reactions = 1
                reaction = 0
                while check_reactions < usercount:
                    if check_reactions >= usercount:
                        break
                    else:
                        try:
                            reaction = await self.client.wait_for(
                                'reaction_add', timeout=30.0, check=lambda reaction, user: reaction.emoji == self.client.checkmarkGlyph(context.guild)
                            )
                            if reaction != None:
                                check_reactions += 1
                            else:
                                break
                        except asyncio.TimeoutError:
                            embededit = discord.Embed(title="Vote Failed.", color=0xff0000)
                            embededit.add_field(name="Kick failed:", value="Not enough players voted.", inline=False)
                            await votemessage.edit(embed=embededit)
                            await votemessage.clear_reactions()

                if check_reactions >= usercount:
                    embededit = discord.Embed(title="Vote Passed!", color=0x00ff00)
                    embededit.add_field(name="Kicking user...", value=target.mention, inline=False)
                    await votemessage.edit(embed=embededit)
                    await votemessage.clear_reactions()
                    await context.author.move_to(None)

                await context.guild.me.edit(nick="")

            # If target is not admin, kick target
            else:
                embed = discord.Embed(title=f"Vote by: {context.author.display_name}", color=0xc6c6c6)
                embed.add_field(name="Kick player:", value=target.mention, inline=False)
                votemessage = await context.send(embed=embed)

                await votemessage.add_reaction(self.client.checkmarkGlyph(context.guild))
                await votemessage.add_reaction(self.client.xmarkGlyph(context.guild))

                check_reactions = 1
                reaction = 0
                while check_reactions < usercount:
                    if check_reactions >= usercount:
                        break
                    else:
                        try:
                            reaction = await self.client.wait_for(
                                'reaction_add', timeout=30.0, check=lambda reaction, user: reaction.emoji == self.client.checkmarkGlyph(context.guild)
                            )
                            if reaction != None:
                                check_reactions += 1
                            else:
                                break
                        except asyncio.TimeoutError:
                            embededit = discord.Embed(title="Vote Failed.", color=0xff0000)
                            embededit.add_field(name="Kick failed:", value="Not enough players voted.", inline=False)
                            await votemessage.edit(embed=embededit)
                            await votemessage.clear_reactions()

                if check_reactions >= usercount:
                    embededit = discord.Embed(title="Vote Passed!", color=0x00ff00)
                    embededit.add_field(name="Kicking user...", value=target.mention, inline=False)
                    await votemessage.edit(embed=embededit)
                    await votemessage.clear_reactions()
                    await target.move_to(None)


# Setup & Link
def setup(client):
    client.add_cog(VCManagement(client))
