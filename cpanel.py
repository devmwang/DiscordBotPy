# Imports
import asyncio
import json
import subprocess
import time
import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, is_owner
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle
from discord_slash import ComponentContext

import reference
import discordCommandOptions

from bot_management import BotManagement

# Class
class CPanel(Cog):
    def __init__(self, client):
        self.client = client

        # * Check applicable settings on initialization
        # Check Price Bot health tracker status and start if necessary
        with open('active_settings.json') as json_file:
            data = json.load(json_file)

            if data['crypto-price-bots']['health-tracker']['enabled'] == True:
                self.check_price_bot_health.start()
        
    # * Control Panel Command
    @cog_ext.cog_slash(name='cpanel', description='Discord Bot Function Control Panel.', guild_ids=reference.guild_ids)
    async def cpanel(self, context: SlashContext):
        title_embed = discord.Embed(title=f'Discord Bot Control Panel', color=0x00ff00)
        await context.reply(embed=title_embed)

        with open('active_settings.json') as settings_json_file:
            settings_data = json.load(settings_json_file)

            with open('cpanel_options.json') as options_json_file:
                options_data = json.load(options_json_file)

                for module in options_data:
                    await context.channel.send(content=f"**Module: {module}**")

                    for option in options_data[module]:
                        option_prop = options_data[module][option]

                        buttons = [create_button(style=option_prop[2][0], label=option_prop[1][0]),
                                    create_button(style=option_prop[2][1], label=option_prop[1][1])]
                        action_row = create_actionrow(*buttons)

                        curr_active_setting = settings_data[option_prop[0][0]][option_prop[0][1]][option_prop[0][2]]
                        conv_curr_active_to_display = option_prop[1][option_prop[3].index(curr_active_setting)]

                        msg = await context.channel.send(content=f"**{option}**: Currently set to __{conv_curr_active_to_display}__.", components=[action_row])

                        try:
                            while True:
                                button_ctx: ComponentContext = await wait_for_component(self.client, components=action_row, timeout=10)
                                
                                # Check that user who clicked button has permissions to change specified setting
                                if (button_ctx.author_id in option_prop[4]):
                                    selector_index = option_prop[1].index(button_ctx.component['label'])
                                    settings_data[option_prop[0][0]][option_prop[0][1]][option_prop[0][2]] = option_prop[3][selector_index]

                                    with open('active_settings.json', 'w') as outfile:
                                        json.dump(settings_data, outfile, indent=4)

                                        await button_ctx.send(content=f"**{option}** updated to __{button_ctx.component['label']}__.")
                                        await msg.edit(components=[])

                                        # CPanel Loop Control
                                        match(option_prop[5]):
                                            case "crypto-price-bot-health-tracker-enabled":
                                                if settings_data[option_prop[0][0]][option_prop[0][1]][option_prop[0][2]]:
                                                    try:
                                                        self.check_price_bot_health.start()
                                                    except RuntimeError:
                                                        pass
                                                else:
                                                    self.check_price_bot_health.stop()
                                else:
                                    await button_ctx.send(content=f"You do not have permission to modify this setting.")
                        except asyncio.TimeoutError:
                            await msg.edit(components=[])

    # * Asynchronous Loops
    # Async Loop for Bot Health Tracker
    @tasks.loop(seconds=30) # Run every 30 seconds
    async def check_price_bot_health(self):
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
            embed.add_field(name="For: ", value="Combined Crypto Price Bots")
            embed.add_field(name="Time: ", value=time.strftime('%I:%M:%S %p', time.localtime()))

            await self.client.logChannel.send(embed=embed)

        # If any of Ryan's bots are offline, trigger a restart using message command
        if ryan_bots_offline:
            TRGeneral = self.client.get_channel(reference.TRGeneralId)
            await TRGeneral.send('auto restart price bots')

            # Log restart command in DiscordBot Control
            embed = discord.Embed(title=f"Triggered Service Restart", color=0x00ff00)
            embed.add_field(name="For: ", value="Single Crypto Price Bots")
            embed.add_field(name="Time: ", value=time.strftime('%I:%M:%S %p', time.localtime()))

            await self.client.logChannel.send(embed=embed)

    # Wait for Cog to be ready before starting loop
    @check_price_bot_health.before_loop
    async def before_check_price_bot_health(self):
        await self.client.wait_until_ready()


# Setup & Link
def setup(client):
    client.add_cog(CPanel(client))
