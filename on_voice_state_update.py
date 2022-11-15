# Imports
import subprocess
import random
import datetime
import discord
from discord.ext.commands import Bot, Cog

import reference


# Class
class OnVoiceStateUpdate(Cog):
    def __init__(self, client: Bot):
        self.client = client

    @Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        if member.id == self.client.admin_id:

            # Movement Sys
            async for audit_log_entry in self.client.get_guild(reference.TR_GUILD_ID).audit_logs(limit=1, action=discord.AuditLogAction.member_move):
                # If last move not by admin or bot, restore original channel
                if (audit_log_entry.user.id not in [315238599761330197, 636013327276965889]):
                    try:
                        moveChannel = self.client.get_channel(before.channel.id)
                        await member.edit(voice_channel=moveChannel)
                    except AttributeError:
                        continue
        
            # Mute Sys
            if after.mute == True:
                await member.edit(mute=False)
        
            # Deafen Sys
            if after.deaf == True:
                await member.edit(deafen=False)


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(OnVoiceStateUpdate(client))
