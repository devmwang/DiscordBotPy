import asyncio
import json
import subprocess
import time
import discord
from discord import app_commands, ui
from discord.ext.commands import Bot, Cog

import reference


class CPanelSubsystemInputs(ui.Button):
    def __init__(self, client, option, index):
        self.client = client
        self.option = option
        self.index = index

        super().__init__(
            label=option[1][index], style=discord.ButtonStyle(option[2][index])
        )

    async def callback(self, interaction: discord.Interaction):
        user_selection = self.option[3][self.index]

        self.client.state[self.option[4]][self.option[5]] = user_selection

        with open("active_settings.json") as settings_json_file:
            settings_data = json.load(settings_json_file)

            old_value = self.option[1][
                self.option[3].index(
                    settings_data[self.option[0][0]][self.option[0][1]][
                        self.option[0][2]
                    ]
                )
            ]

            settings_data[self.option[0][0]][self.option[0][1]][
                self.option[0][2]
            ] = user_selection

            with open("active_settings.json", "w") as outfile:
                json.dump(settings_data, outfile, indent=4)

        new_value = self.option[1][self.index]

        await interaction.response.send_message(
            f"**Option updated successfully** ({old_value} -> {new_value})"
        )
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

        super().__init__(
            placeholder="Choose a subsystem to modify:",
            min_values=1,
            max_values=1,
            options=select_options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.callback_interaction = interaction

        response_embed = discord.Embed(
            title=f"{self.values[0]} Subsystem",
            color=discord.Color.from_rgb(47, 49, 54),
        )

        await interaction.response.send_message(embed=response_embed)

        self.option_messages = []

        # Read curr values for cpanel display
        with open("active_settings.json") as settings_json_file:
            settings_data = json.load(settings_json_file)

        for option in self.options_data[self.values[0]]:
            option_dict = self.options_data[self.values[0]][option]
            curr_value = option_dict[1][
                option_dict[3].index(
                    settings_data[option_dict[0][0]][option_dict[0][1]][
                        option_dict[0][2]
                    ]
                )
            ]

            msg = await interaction.channel.send(
                content=f"**{option}:** Currently set to **{curr_value}**",
                view=CPanelSubsystemView(self.client, option_dict),
            )

            self.option_messages.append(msg)

        # Delete all messages after button timeout (180 seconds default)
        await asyncio.sleep(180)

        for msg in self.option_messages:
            await msg.delete()

        await interaction.delete_original_response()

        await self.interaction.delete_original_response()


class CPanelView(ui.View):
    def __init__(self, client, options_data, interaction):
        super().__init__()

        self.add_item(CPanelSelect(client, options_data, interaction))


class CPanel(Cog):
    def __init__(self, client: Bot):
        self.client = client

    # * Control Panel Command
    @app_commands.command(
        name="cpanel", description="Discord Bot System Control Panel."
    )
    async def cpanel(self, interaction: discord.Interaction):
        with open("cpanel_options.json") as options_json_file:
            options_data = json.load(options_json_file)

            cpanel_view = CPanelView(self.client, options_data, interaction)

        await interaction.response.send_message(view=cpanel_view)


async def setup(client):
    await client.add_cog(CPanel(client))
