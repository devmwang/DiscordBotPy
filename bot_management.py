# Imports
import asyncio
import json
import subprocess
import time
import discord
from discord.ext import tasks
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference

# Class
class BotManagement(Cog):
    def __init__(self, client: Bot):
        self.client = client

        # * Initialize subsystem global state
        with open('active_settings.json') as json_file:
            data = json.load(json_file)

            self.client.state["bot_management"]["price-bot-life-support-enabled"] = data['price-bots']['life-support']['enabled']

        # * Initialize Loops
        self.check_price_bot_status.start()


    @app_commands.command(name="restartpricebots")
    async def restartpricebots(self, interaction: discord.Interaction):
        try:
            pipe = subprocess.Popen("sudo systemctl restart crypto-price-bots", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = pipe.communicate()
            error = err.decode()
            response = out.decode()
            combined = response + error
            if combined == "":
                msg = await interaction.response.send_message(f"{self.client.checkmarkGlyph(interaction.guild)} Crypto price bots restarted successfully.")
                await asyncio.sleep(5)
                await msg.delete()
            else:
                await interaction.response.send_message(f"```{combined}```")
        except discord.errors.HTTPException as _e:
            await interaction.response.send_message(self.client.xmarkGlyph(interaction.guild), _e)

    
    # * Life Support Check Loop
    @tasks.loop(seconds=3)
    async def check_price_bot_status(self):
        if self.client.state["bot_management"]["price-bot-life-support-enabled"] == False:
            return

        # Get guild
        guild = self.client.get_guild(696082479752413274)

        # Get roles for my bots and Ryan's bots
        my_bots_role = guild.get_role(reference.my_price_bots_role_id)
        ryan_bots_role = guild.get_role(reference.ryan_price_bots_role_id)

        # Set local vars to track
        my_bots_offline = False
        ryan_bots_offline = False

        # Check if any of my bots are offline
        for member in my_bots_role.members:
            if member.raw_status == "offline":
                my_bots_offline = True

        # Check if any of Ryan's bots are offline
        for member in ryan_bots_role.members:
            if member.raw_status == "offline":
                ryan_bots_offline = True

        # If any of my bots are offline, trigger a service restart
        if my_bots_offline:
            subprocess.Popen("sudo service crypto-price-bots restart", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Log restart command in DiscordBot Control
            embed = discord.Embed(title=f"Triggered Service Restart", color=0x00ff00)
            embed.add_field(name="For: ", value="Michael's Crypto Price Bots")
            embed.add_field(name="Time: ", value=time.strftime('%I:%M:%S %p', time.localtime()))

            await self.client.logChannel.send(embed=embed)

        # If any of Ryan's bots are offline, trigger a restart using message command
        if ryan_bots_offline:
            TRGeneral = self.client.get_channel(reference.TRGeneralId)
            await TRGeneral.send('auto restart price bots')

            # Log restart command in DiscordBot Control
            embed = discord.Embed(title=f"Triggered Service Restart", color=0x00ff00)
            embed.add_field(name="For: ", value="Ryan's Crypto Price Bots")
            embed.add_field(name="Time: ", value=time.strftime('%I:%M:%S %p', time.localtime()))

            await self.client.logChannel.send(embed=embed)

    # Wait for extension to be ready before starting loop
    @check_price_bot_status.before_loop
    async def before_check_price_bot_status(self):
        await self.client.wait_until_ready()


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(BotManagement(client))
