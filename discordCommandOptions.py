from os import name
from discord_slash.utils.manage_commands import create_option, create_choice

# Main
loadOpts = [
    create_option(name='cog', description='Name of cog to load.', option_type=3, required=True)
]

unloadOpts = [
    create_option(name='cog', description='Name of cog to unload.', option_type=3, required=True)
]

reloadOpts = [
    create_option(name='cog', description='Name of cog to reload.', option_type=3, required=True)
]

# Exec
exec = [
    create_option(name='arguments', description='Command to execute in terminal.', option_type=3, required=True)
]

# FTX
quickprice = [
    create_option(name='ticker', description='Ticker of asset to get price for.', option_type=3, required=True)
]

timeRange = [
    create_option(name='hours', description='Time range to calculate lending profit from.', option_type=4, required=False)
]

coin = [
    create_option(name='coin', description='Specific coin data to display.', option_type=3, required=False)
]

# Uniswap
pairOpts = [
    create_option(name='target', description='Enter the target\'s ticker.', option_type=3, required=True),
    create_option(name='base', description='Enter the base\'s ticker (Defaults to USDC).', option_type=3, required=False)
]

addToken = [
    create_option(name='ticker', description='Ticker of contract to add.', option_type=3, required=True),
    create_option(name='address', description='Address of contract to add.', option_type=3, required=True),
    create_option(name='decimals', description='Number of decimals that the contract uses.', option_type=4, required=True),
    create_option(name='name', description='Full name of token to add.', option_type=3, required=False)
]

removeToken = [
    create_option(name='ticker', description='Ticker of contract to add.', option_type=3, required=True)
]

modifyToken = [
    create_option(name='ticker', description='Ticker of contract to modify.', option_type=3, required=True),
    create_option(name='target', description='Property of entry to modify.', option_type=3, required=True),
    create_option(name='value', description='Value to assign to targeted property.', option_type=3, required=True)
]

# Others
counters = [
    create_option(name='target', description='User to acquire data for.', option_type=9, required=True)
]

presence = [
    create_option(name='action', description='Action', option_type=3, required=True, choices=[
        create_choice(name='Clear', value='clear'),
        create_choice(name='Playing...', value='play'),
        create_choice(name='Watching...', value='watch'),
        create_choice(name='Listening to...', value='listen'),
        create_choice(name='Competing in...', value='compete')
    ]),
    create_option(name='activity', description='Name of activity.', option_type=3, required=False)
]

clearMsg = [
    create_option(name='amount', description='Number of messages to remove.', option_type=4, required=False)
]

createBuddy = [
    create_option(name='limit', description='Maximum number of characters.', option_type=4, required=True)
]

# VC Management
votekick = [
    create_option(name='target', description='Target to clap.', option_type=9, required=True)
]

# Clap
clap = [
    create_option(name='target', description='Target to clap.', option_type=9, required=True),
    create_option(name='amount', description='Times to clap user.', option_type=4, required=False)
]