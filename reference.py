import discord

startup_extensions = ["jishaku", "on_message", "on_voice_state_update", "exec", "cpanel", "bot_management", "others", "ftx", "clap"]
# startup_cogs = ["jishaku", "exec", "cpanel", "bot_management", "on_message", "on_voice_state_update", "ftx", "channel_logging", "others", "vc_management", "clap"]

# DiscordBot Control
CONTROL_GUILD_ID = 746647021561053215
CONTROL_GUILD = discord.Object(id=CONTROL_GUILD_ID)

CONTROL_LOG_ID = 746648561424269392

# TR
TR_GUILD_ID = 696082479752413274
TR_GUILD = discord.Object(id=TR_GUILD_ID)

TR_GUILD_GENERAL_ID = 918663904215859312

# Reference Values
cmd_msg_delete_cooldown = 5

# Relevant IDs
TRGeneralId = 696082479752413277

# Price Bot Health Tracker
my_price_bots_role_id = 944000887444107344
ryan_price_bots_role_id = 944001011775852585

# Enhanced Audit Log System
eal_monitored_servers = [696082479752413274]

# FTX Module
ftx_endpoint = 'https://ftx.com/api/'

# Uniswap Module
# uniswap_version = 3
# eth_node = 'https://mainnet.infura.io/v3/08f42afb29804e18ab2b12d2b418661f'
