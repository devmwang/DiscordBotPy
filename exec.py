# Imports
import subprocess
import discord
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions


# Clap
class Exec(Cog):
    def __init__(self, client):
        self.client = client

    # Exec Terminal Commands
    @cog_ext.cog_slash(name='exec', options=discordCommandOptions.exec, guild_ids=reference.guild_ids)
    async def exec(self, context: SlashContext, arguments: str):
        if context.author.id == self.client.admin_id:
            try:
                pipe = subprocess.Popen(arguments, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = pipe.communicate()
                error = err.decode()
                response = out.decode()
                combined = response + error
                if combined == "":
                    await context.send(f"{self.client.checkmarkGlyph(context.guild)} Command executed with no output.")
                else:
                    await context.send(f"```{combined}```")
            except discord.errors.HTTPException as _e:
                await context.send(self.client.xmarkGlyph(context.guild), _e)
        else:
            await context.send(f"You do not have permission to use this command. {self.client.xmarkGlyph(context.guild)}")


# Setup & Link
def setup(client):
    client.add_cog(Exec(client))
