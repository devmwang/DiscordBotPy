# Imports
from web3.main import Web3
from uniswap import Uniswap
import json
import discord
from discord import colour
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext

import reference
import discordCommandOptions


# Eth Chain Details
address = None
private_key = None

# Initialize Uniswap
uni = Uniswap(address=address,private_key=private_key,version=reference.uniswap_version,provider=reference.eth_node)


class Uni(Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_slash(name='uniswap', description='Get current token prices from UniSwap V3.', options=discordCommandOptions.pairOpts, guild_ids=reference.guild_ids)
    async def uniswap(self, context: SlashContext, target: str, base: str = 'usdc'):
        with open('tokens.json') as json_file:
            data = json.load(json_file)

            target = target.upper()
            base = base.upper()

            if (target in data['tokens'] and base in data['tokens']):
                cost = str(uni.get_price_input(Web3.toChecksumAddress(data['tokens'][target]['address']), Web3.toChecksumAddress(data['tokens'][base]['address']), 10**(data['tokens'][target]['decimals'])))

                if data['tokens'][base]['decimals'] > len(cost):
                    diff = data['tokens'][base]['decimals'] - len(cost)
                    formatted_cost = '0.' + '0' * diff + cost
                else:
                    formatted_cost = cost[:-data['tokens'][base]['decimals']] + '.' + cost[-data['tokens'][base]['decimals']:]

                await context.send(f'Cost of {target}: {round(float(formatted_cost), 5)} {base} on Uniswap V{reference.uniswap_version }')
            else:
                await context.send('One of the parameters entered could not be parsed. Please try again.')

    @cog_ext.cog_slash(name='addtoken', description='Add token to contract list.', options=discordCommandOptions.addToken, guild_ids=reference.guild_ids)
    async def addtoken(self, context: SlashContext, ticker: str, address: str, decimals: int, name: str = None):
        with open('tokens.json') as json_file:
            data = json.load(json_file)

            if (ticker.upper() not in data['tokens']):
                if (name is None):
                    data['tokens'][ticker.upper()] = {
                        'address': address,
                        'decimals': decimals
                    }
                else:
                    data['tokens'][ticker.upper()] = {
                        'address': address,
                        'decimals': decimals,
                        'name': name.capitalize()
                    }

                with open('tokens.json', 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                
                await context.send(f'{ticker.upper()} added successfully. {self.client.checkmarkGlyph(context.guild)}')
            else:
                await context.send(f'{ticker.upper()} already exists. {self.client.xmarkGlyph(context.guild)}')
    
    @cog_ext.cog_slash(name='removetoken', description='Remove token from contract list.', options=discordCommandOptions.removeToken, guild_ids=reference.guild_ids)
    async def removetoken(self, context: SlashContext, ticker: str):
        with open('tokens.json') as json_file:
            data = json.load(json_file)

            if (ticker.upper() in data['tokens']):
                del data['tokens'][ticker.upper()]
                
                with open('tokens.json', 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                
                await context.send(f'{ticker.upper()} deleted. {self.client.checkmarkGlyph(context.guild)}')
            else: 
                await context.send(f'{ticker.upper()} could not be found. Please try again. {self.client.xmarkGlyph(context.guild)}')

    @cog_ext.cog_slash(name='modifytoken', description='Edit token entry in contract list.', options=discordCommandOptions.modifyToken, guild_ids=reference.guild_ids)
    async def modifytoken(self, context: SlashContext, ticker: str, target: str, value: str):
        with open('tokens.json') as json_file:
            data = json.load(json_file)

            if (ticker.upper() in data['tokens']):
                match target.lower():
                    case 'address':
                        data['tokens'][ticker.upper()]['address'] = value
                    case 'decimals':
                        data['tokens'][ticker.upper()]['decimals'] = int(value)
                    case 'name':
                        data['tokens'][ticker.upper()]['name'] = value
                
                with open('tokens.json', 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                
                await context.send(f'{ticker.upper()} updated successfully. {self.client.checkmarkGlyph(context.guild)}')
            else: 
                await context.send(f'{ticker.upper()} could not be found. Please try again. {self.client.xmarkGlyph(context.guild)}')

    @cog_ext.cog_slash(name='listtokens', description='List all tokens stored.', guild_ids=reference.guild_ids)
    async def listtokens(self, context: SlashContext):
        with open('tokens.json') as json_file:
            data = json.load(json_file)

            embed = discord.Embed(title=f'Saved ERC-20 Tokens', color=0x00ff00)

            for token in data['tokens']:
                if ('name' in data['tokens'][token]):
                    embed.add_field(name=token, value=data['tokens'][token]['name'], inline=False)
                else:
                    embed.add_field(name=token, value=token, inline=False)

            await context.send(embed=embed)                


# Setup & Link
def setup(client):
    client.add_cog(Uni(client))
