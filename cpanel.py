import asyncio
import json
import subprocess
import time
from turtle import title
import discord
from discord import app_commands, ui
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

import reference


class CPanelSubsystemInputs(ui.Button):
    def __init__(self, client, option, index):
        self.client = client
        self.option = option
        self.index = index

        super().__init__(label=option[1][index], style=discord.ButtonStyle(option[2][index]))

    async def callback(self, interaction: discord.Interaction):
        with open('active_settings.json') as settings_json_file:
            settings_data = json.load(settings_json_file)

            settings_data[self.option[0][0]][self.option[0][1]][self.option[0][2]] = self.option[3][self.index]

            with open('active_settings.json', 'w') as outfile:
                json.dump(settings_data, outfile, indent=4)

        await interaction.response.send_message("Option updated successfully.")
        await asyncio.sleep(reference.cmd_msg_delete_cooldown)
        await interaction.delete_original_response()


class CPanelSubsystemView(ui.View):
    def __init__(self, client, option):
        super().__init__()

        for index in range(len(option[1])):
            self.add_item(CPanelSubsystemInputs(client, option, index))


class CPanelSelect(ui.Select):
    def __init__(self, client, options_data, interaction):
        self.client = client
        self.options_data = options_data
        self.interaction = interaction

        select_options = []

        for subsystem in options_data:
            select_options.append(discord.SelectOption(label=subsystem))

        super().__init__(placeholder='Choose a subsystem to modify:', min_values=1, max_values=1, options=select_options)

    async def callback(self, interaction: discord.Interaction):
        response_embed = discord.Embed(title=f"{self.values[0]} Subsystem", color=discord.Color.from_rgb(47, 49, 54))

        await interaction.response.send_message(embed=response_embed)

        option_messages = []

        # Read curr values for cpanel display
        with open('active_settings.json') as settings_json_file:
            settings_data = json.load(settings_json_file)

        for option in self.options_data[self.values[0]]:
            option_dict = self.options_data[self.values[0]][option]
            curr_value = option_dict[1][option_dict[3].index(settings_data[option_dict[0][0]][option_dict[0][1]][option_dict[0][2]])]

            msg = await interaction.channel.send(content=f"**{option}:** Currently set to **{curr_value}**", view = CPanelSubsystemView(self.client, option_dict))
            option_messages.append(msg)

        # Delete all messages after button timeout (180 seconds default)
        await asyncio.sleep(180)

        for msg in option_messages:
            await msg.delete()
        
        await interaction.delete_original_response()

        await self.interaction.delete_original_response()


class CPanelView(ui.View):
    def __init__(self, client, options_data, interaction):
        super().__init__()

        self.add_item(CPanelSelect(client, options_data, interaction))


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
    @app_commands.command(name='cpanel', description='Discord Bot System Control Panel.')
    async def cpanel(self, interaction: discord.Interaction):
        with open('cpanel_options.json') as options_json_file:
            options_data = json.load(options_json_file)

            cpanel_view = CPanelView(self.client, options_data, interaction)

        await interaction.response.send_message(view=cpanel_view)


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


async def setup(client):
    await client.add_cog(CPanel(client))
