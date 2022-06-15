# Imports
import subprocess
import random
import datetime
import discord
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference


# Class
class OnVoiceStateUpdate(Cog):
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Movement Sys
        if member.id == self.client.admin_id:
            # Get Robean Guild
            guild = self.client.get_guild(reference.theRobeanGuildId)

            # Check latest audit log
            async for audit_log_entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_move):
                # If last move not by admin or bot, restore original channel
                if (audit_log_entry.user.id not in [315238599761330197, 636013327276965889]):
                    try:
                        moveChannel = self.client.get_channel(before.channel.id)
                        await member.edit(voice_channel=moveChannel)
                    except AttributeError:
                        continue
        
        # Mute Sys
        if member.id == self.client.admin_id:
            muteval = after.mute
            if muteval == True:
                await member.edit(mute=False)
        
        # Deafen Sys
        if member.id == self.client.admin_id:
            deafval = after.deaf
            if deafval == True:
                await member.edit(deafen=False)


# Setup & Link
def setup(client):
    client.add_cog(OnVoiceStateUpdate(client))
