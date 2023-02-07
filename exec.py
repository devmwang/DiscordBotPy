import subprocess
import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference

# test


class Exec(Cog):
    def __init__(self, client: Bot):
        # super()._inject(bot=client, override=False)

        self.client = client

    # Exec Terminal Commands
    @app_commands.command(name="exec", description="Execute shell command on host.")
    @app_commands.describe(arguments="Shell command to execute.")
    async def exec(self, interaction: discord.Interaction, arguments: str):
        if interaction.user.id == self.client.admin_id:
            try:
                pipe = subprocess.Popen(
                    arguments,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                out, err = pipe.communicate()
                error = err.decode()
                response = out.decode()
                combined = response + error
                if combined == "":
                    await interaction.response.send_message(
                        f"{self.client.checkmarkGlyph(interaction.guild)} Command executed with no output."
                    )
                else:
                    await interaction.response.send_message(f"```{combined}```")
            except discord.errors.HTTPException as _e:
                await interaction.response.send_message(
                    self.client.xmarkGlyph(interaction.guild), _e
                )
        else:
            await interaction.response.send_message(
                f"You do not have permission to use this command. {self.client.xmarkGlyph(interaction.guild)}"
            )


async def setup(client: Bot):
    await client.add_cog(Exec(client))
