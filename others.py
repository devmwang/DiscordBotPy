# Imports
import asyncio
import os
import datetime
import json
import subprocess
from time import strftime
import discord
from PIL import Image
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions


# Class
class Others(Cog):
    def __init__(self, client):
        self.client = client


    # Commands
    # Counters Tally Display
    @cog_ext.cog_slash(name="counter", options=discordCommandOptions.counters, guild_ids=reference.guild_ids)
    async def counter(self, context: SlashContext, target, word):
        with open('counters.json') as counters_file:
            counters_data = json.load(counters_file)

            embed = discord.Embed(title=f'FTX Quickprice', color=0x00ff00)
            embed.add_field(name='User:', value=context.guild.get_member(int(target)).mention)
            embed.add_field(name='Word:', value=word)

            try:
                curr_total = counters_data["word_counters"][word][target]
            except KeyError:
                curr_total = 0
            
            embed.add_field(name='Current Total:', value=curr_total)

            message = await context.send(embed=embed)

    # Shafting Level Heat Map
    @cog_ext.cog_slash(name="heatmap", guild_ids=reference.guild_ids)
    async def heatmap(self, context: SlashContext):
        message = await context.send('Generating heatmap, please wait (This process can take up to 15 seconds)')
        options = Options()
        options.headless = True
        options.add_argument("window-size=2560,1440")

        match platform.system():
            case 'Windows':
                driverPath = 'ChromeDriver/windows_chromedriver.exe'
            case 'Darwin':
                driverPath = 'ChromeDriver/m1_chromedriver'
            case 'Linux':
                driverPath = 'ChromeDriver/linux_chromedriver'

        ssDriver = webdriver.Chrome(options=options, executable_path=driverPath)

        ssDriver.get('https://coin360.com/')
        wait = WebDriverWait(ssDriver, 10)
        wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "StickyCorner__Close"))).click()
        wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "TopLeaderboard__Close"))).click()
        await asyncio.sleep(0.1)
        ssDriver.save_screenshot('shaftmap.png')
        ssDriver.quit()

        shaftmap = Image.open('shaftmap.png')
        shaftmap = shaftmap.crop((0, 80, 2560, 1416))
        shaftmap.save('shaftmap.png')

        file = discord.File("shaftmap.png")
        await message.edit(content=f"Heatmap generated at {datetime.datetime.fromtimestamp(os.path.getmtime('shaftmap.png')).strftime('%I:%M %p')}.", file=file)


    # Set Presence
    @cog_ext.cog_slash(name="setPresence", options=discordCommandOptions.presence, guild_ids=reference.guild_ids)
    async def setPresence(self, context: SlashContext, action, activity = None):
        if context.author.id == self.client.admin_id:
            if (action == "clear"):
                await self.client.change_presence()
                await context.send(f"Presence cleared successfully. {self.client.checkmarkGlyph(context.guild)}")
            elif (action == "play"):
                await self.client.change_presence(activity=discord.Game(activity))
                await context.send(f"Presence changed successfully. {self.client.checkmarkGlyph(context.guild)}")
            elif (action == "watch"):
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
                await context.send(f"Presence changed successfully. {self.client.checkmarkGlyph(context.guild)}")
            elif (action == "listen"):
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))
                await context.send(f"Presence changed successfully. {self.client.checkmarkGlyph(context.guild)}")
            elif (action == "compete"):
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=activity))
                await context.send(f"Presence changed successfully. {self.client.checkmarkGlyph(context.guild)}")
            else:
                await context.send("An error occurred while parsing your request. Please try again.")
        else:
            await context.send(f"You do not have permission to use this command. {self.client.xmarkGlyph(context.guild)}")

    # Message Clap Command
    @cog_ext.cog_slash(name='clearmsg', description='Delete messages from channel.', options=discordCommandOptions.clearMsg, guild_ids=reference.guild_ids)
    async def clearmsg(self, context: SlashContext, amount = 5):
        if context.author.id == self.client.admin_id:
            self.client.deleted_messages = []
            async for message in context.channel.history(limit=int(amount)):
                self.client.deleted_messages.append(message)
            self.client.deleted_messages.reverse()
            
            await context.channel.delete_messages(self.client.deleted_messages)
            await context.send(f"{amount} messages deleted. {self.client.checkmarkGlyph(context.guild)}")
        else:
            await context.send(f"Access denied - You do not have permission to access this command. {self.client.xmarkGlyph(context.guild)}")

    # Restore Message Command
    @cog_ext.cog_slash(name='restoremsg', description='Restore last batch of deleted messages.', guild_ids=reference.guild_ids)
    async def restoremsg(self, context: SlashContext):
        if context.author.id == self.client.admin_id:
            if len(self.client.deleted_messages) == 0:
                await context.send(f"No deleted messages currently cached.")
                return

            for message in self.client.deleted_messages:
                # If message contained embeds, resend embed with modified title
                if not not message.embeds:
                    for embed in message.embeds:
                        if embed.title == discord.Embed.Empty:
                            modified_embed_title = "Restored Embed"
                        else:
                            modified_embed_title = f"Restored Embed: {embed.title}"
                        embed.title = modified_embed_title
                    
                        await context.channel.send(embed=embed)

                # If message has no content and no attachments, don't send
                if not not message.content or not not message.attachments:
                    # Check if message has content
                    if not message.content:
                        embed = discord.Embed(description="No Message Content", color=0x2f3136)
                    else:
                        embed = discord.Embed(description=message.content, color=0x2f3136)
                    
                    embed.set_author(name=message.author, icon_url=message.author.avatar_url)

                    # Check if message has attachments
                    if not not message.attachments:
                        for i in message.attachments:
                            embed.add_field(name="File", value=i.url)
                            if not message.content:
                                embed.description = "Restored Attachment"

                    await context.channel.send(embed=embed)
            
            msg = await context.send(f"Messages restored. {self.client.checkmarkGlyph(context.guild)}")
            await asyncio.sleep(reference.cmd_msg_delete_cooldown)
            await msg.delete()
            self.client.deleted_messages = []
        else:
            msg = await context.send(f"Access denied - You do not have permission to access this command. {self.client.xmarkGlyph(context.guild)}")
            await asyncio.sleep(reference.cmd_msg_delete_cooldown)
            await msg.delete()

    # Buddy Creator Command
    @cog_ext.cog_slash(name='createbuddy', options=discordCommandOptions.createBuddy, guild_ids=reference.guild_ids)
    async def createbuddy(self, context: SlashContext, limit):
        if (int(limit) < 16):
            msg = await context.send("Minimum limit is 16.")
            await asyncio.sleep(reference.cmd_msg_delete_cooldown)
            await msg.delete()
        else:
            final = ""
            buddy = "BUDDY "
            u = "that's you"
            while (len(final) < (int(limit) - 15)):
                final += buddy
            msg = await context.send(final + u)
            await asyncio.sleep(reference.cmd_msg_delete_cooldown)
            await msg.delete()


# Setup & Link
def setup(client):
    client.add_cog(Others(client))
