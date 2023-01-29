import json
import subprocess
import discord
from discord.ext.commands import Bot, Cog

import reference


class OnMessage(Cog):
    def __init__(self, client: Bot):
        self.client = client

    # Listener
    @Cog.listener()
    async def on_message(self, message):
        # Exec OS Level Commands with Sudo
        if message.content[0:4] == "sudo" and message.author.bot == False:
            if message.author.id == self.client.admin_id:
                try:
                    pipe = subprocess.Popen(
                        message.content,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    out, err = pipe.communicate()
                    error = err.decode()
                    response = out.decode()
                    combined = response + error
                    if combined == "":
                        await message.reply(
                            f"{self.client.checkmarkGlyph(message.guild)} Command executed with no output."
                        )
                    else:
                        await message.reply(f"```{combined}```")
                except discord.errors.HTTPException as _e:
                    await message.reply(self.client.xmarkGlyph(message.guild), _e)
            else:
                await message.reply(
                    f"You do not have permission to use this command. {self.client.xmarkGlyph(message.guild)}"
                )

        # Chat Filter
        filtered_seqs = ["Did you mean"]

        for seq in filtered_seqs:
            if seq in message.content:
                await message.delete()


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(OnMessage(client))
