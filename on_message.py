# Imports
import asyncio
import json
import subprocess
import random
import discord
from discord.ext.commands import Bot, Cog, is_owner
from discord_slash import cog_ext, SlashContext

import reference


# Class
class OnMessage(Cog):
    def __init__(self, client):
        self.client = client

    # Listener
    @Cog.listener()
    async def on_message(self, message):
        # Exec OS Level Commands with Sudo
        if message.content[0:4] == "sudo" and message.author.bot == False:            
            if message.author.id == self.client.admin_id:
                try:
                    pipe = subprocess.Popen(message.content, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = pipe.communicate()
                    error = err.decode()
                    response = out.decode()
                    combined = response + error
                    if combined == "":
                        await message.reply(f"{self.client.checkmarkGlyph(message.guild)} Command executed with no output.")
                    else:
                        await message.reply(f"```{combined}```")
                except discord.errors.HTTPException as _e:
                    await message.reply(self.client.xmarkGlyph(message.guild), _e)
            else:
                await message.reply(f"You do not have permission to use this command. {self.client.xmarkGlyph(message.guild)}")

        # Word Counters (Tracks the number of times a user uses a word)
        if "slay" in message.content:
            with open('counters.json') as counters_file:
                counters_data = json.load(counters_file)
                
                try:
                    counters_data["word_counters"]["slay"][str(message.author.id)] += 1
                except KeyError:
                    counters_data["word_counters"]["slay"][str(message.author.id)] = 1

                with open('counters.json', 'w') as outfile:
                    json.dump(counters_data, outfile, indent=4)


# Setup & Link
def setup(client):
    client.add_cog(OnMessage(client))
