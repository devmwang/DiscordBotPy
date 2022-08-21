# Imports
import asyncio
import os
import datetime
import json
from pydoc import describe
import subprocess
from time import strftime
import platform
import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference


# Class
class Others(Cog):
    def __init__(self, client: Bot):
        self.client = client


    @app_commands.command(name='clearmsg', description='Delete messages from channel.')
    @app_commands.describe(amount="Number of messages to clear.")
    async def clearmsg(self, interaction: discord.Interaction, amount: int = 5):
        await interaction.response.defer()

        if interaction.user.id == self.client.admin_id:
            self.client.deleted_messages = []
            async for message in interaction.channel.history(limit=amount+1):
                self.client.deleted_messages.append(message)
            self.client.deleted_messages.reverse()
            
            await interaction.channel.delete_messages(self.client.deleted_messages)
            await interaction.channel.send(f"{amount} message{'s' if amount != 1 else ''} deleted. {self.client.checkmarkGlyph(interaction.guild)}")
        else:
            await interaction.channel.send(f"Access denied - You do not have permission to access this command. {self.client.xmarkGlyph(interaction.guild)}")


    @app_commands.command(name='restoremsg', description='Restore last batch of deleted messages.')
    async def restoremsg(self, interaction: discord.Interaction):
        if interaction.user.id == self.client.admin_id:
            if len(self.client.deleted_messages) == 0:
                await interaction.response.send_message(f"No deleted messages currently cached.")
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
                    
                        await interaction.channel.send(embed=embed)

                # If message has no content and no attachments, don't send
                if not not message.content or not not message.attachments:
                    # Check if message has content
                    if not message.content:
                        embed = discord.Embed(description="No Message Content", color=0x2f3136)
                    else:
                        embed = discord.Embed(description=message.content, color=0x2f3136)
                    
                    embed.set_author(name=message.author, icon_url=message.author.avatar)

                    # Check if message has attachments
                    if not not message.attachments:
                        for i in message.attachments:
                            embed.add_field(name="File", value=i.url)
                            if not message.content:
                                embed.description = "Restored Attachment"

                    await interaction.channel.send(embed=embed)
            
            await interaction.response.send_message(f"Messages restored. {self.client.checkmarkGlyph(interaction.guild)}")
            await asyncio.sleep(reference.cmd_msg_delete_cooldown)
            await interaction.delete_original_response()
            self.client.deleted_messages = []
        else:
            await interaction.response.send_message(f"Access denied - You do not have permission to access this command. {self.client.xmarkGlyph(interaction.guild)}")
            await asyncio.sleep(reference.cmd_msg_delete_cooldown)
            await interaction.delete_original_response()
    

    @app_commands.command(name="setpresence")
    @app_commands.describe(action="Action", activity="Activity label")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Clear", value="clear"),
            app_commands.Choice(name="Playing", value="play"),
            app_commands.Choice(name="Watching", value="watch"),
            app_commands.Choice(name="Listening to", value="listen"),
            app_commands.Choice(name="Competing in", value="compete"),
        ]
    )
    async def setpresence(self, interaction: discord.Interaction, action: app_commands.Choice[str], activity: str = None):
        if interaction.user.id == self.client.admin_id:
            action = action.value

            if (action == "clear"):
                await self.client.change_presence()
                await interaction.response.send_message(f"Presence cleared successfully. {self.client.checkmarkGlyph(interaction.guild)}")
            elif (action == "play"):
                await self.client.change_presence(activity=discord.Game(activity))
                await interaction.response.send_message(f"Presence changed successfully. {self.client.checkmarkGlyph(interaction.guild)}")
            elif (action == "watch"):
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
                await interaction.response.send_message(f"Presence changed successfully. {self.client.checkmarkGlyph(interaction.guild)}")
            elif (action == "listen"):
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))
                await interaction.response.send_message(f"Presence changed successfully. {self.client.checkmarkGlyph(interaction.guild)}")
            elif (action == "compete"):
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=activity))
                await interaction.response.send_message(f"Presence changed successfully. {self.client.checkmarkGlyph(interaction.guild)}")
        else:
            await interaction.response.send_message(f"You do not have permission to use this command. {self.client.xmarkGlyph(interaction.guild)}")


    # @app_commands.command(name="heatmap", guild_ids=reference.guild_ids)
    # async def heatmap(self, interaction: discord.Interaction):
    #     message = await context.send('Generating heatmap, please wait (This process can take up to 15 seconds)')
    #     options = Options()
    #     options.headless = True
    #     options.add_argument("window-size=2560,1440")

    #     match platform.system():
    #         case 'Windows':
    #             driverPath = 'ChromeDriver/windows_chromedriver.exe'
    #         case 'Darwin':
    #             driverPath = 'ChromeDriver/m1_chromedriver'
    #         case 'Linux':
    #             driverPath = 'ChromeDriver/linux_chromedriver'

    #     ssDriver = webdriver.Chrome(options=options, executable_path=driverPath)

    #     ssDriver.get('https://coin360.com/')
    #     wait = WebDriverWait(ssDriver, 10)
    #     wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "StickyCorner__Close"))).click()
    #     wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "TopLeaderboard__Close"))).click()
    #     await asyncio.sleep(0.1)
    #     ssDriver.save_screenshot('shaftmap.png')
    #     ssDriver.quit()

    #     shaftmap = Image.open('shaftmap.png')
    #     shaftmap = shaftmap.crop((0, 80, 2560, 1416))
    #     shaftmap.save('shaftmap.png')

    #     file = discord.File("shaftmap.png")
    #     await message.edit(content=f"Heatmap generated at {datetime.datetime.fromtimestamp(os.path.getmtime('shaftmap.png')).strftime('%I:%M %p')}.", file=file)


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(Others(client))
