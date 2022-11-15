# Imports
import os
import time
import socket
import hmac
import requests
import json
from typing import Optional, Dict, Any
from requests import Request, Session, Response
import urllib3.util.connection as urllib3_cn
import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import reference


_session = Session()

# * Set IPv4 Req Only
def allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family


# * RESTful Functions
def get(path: str, params: Optional[Dict[str, Any]] = None):
    return _request('GET', path, params=params)


def post(path: str, params: Optional[Dict[str, Any]] = None):
    return _request('POST', path, json=params)


def delete(path: str, params: Optional[Dict[str, Any]] = None):
    return _request('DELETE', path, json=params)


def _request(method: str, path: str, **kwargs):
    request = Request(method, reference.ftx_endpoint + path, **kwargs)

    _sign_request(request)
    response = _session.send(request.prepare())
    return _process_response(response)


def _sign_request(request: Request):
    ts = int(time.time() * 1000)
    prepared = request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
    if prepared.body:
        signature_payload += prepared.body
    signature = hmac.new(os.getenv('FTX_API_SECRET').encode(), signature_payload, 'sha256').hexdigest()
    request.headers['FTX-KEY'] = os.getenv('FTX_API_KEY')
    request.headers['FTX-SIGN'] = signature
    request.headers['FTX-TS'] = str(ts)


def _process_response(response: Response):
    try:
        data = response.json()
    except ValueError:
        response.raise_for_status()
        raise
    else:
        if not data['success']:
            return {'id': 'ERROR', 'data': data['error']}
        return {'id': 'SUCCESS', 'data': data['result']}


def createErrorEmbed(error: str):
    embed = discord.Embed(title=f'FTX Error', color=0xff0000)
    embed.add_field(name='Error: ', value=error)

    return embed


def parseLargeValues(volume: int):
    if volume > 10**6:
        return [volume/(10**6), "Million"]
    elif volume > 10**3:
        return [volume/(10**3), "Thousand"]


class FTX(Cog):
    def __init__(self, client: Bot):
        self.client = client

    @app_commands.command(name='quickprice', description='Get current USD cost of any perpetual contract on FTX.')
    @app_commands.describe(ticker="Ticker of asset to get price for.")
    async def quickprice(self, interaction: discord.Interaction, ticker: str):
        response = requests.get(f"https://ftx.com/api/markets/{ticker}-PERP")
        data = json.loads(response.content)
        price = float(data['result']['last'])
        volume_24h = float(data['result']['volumeUsd24h'])
        percent_change_1h = float(data['result']['change1h']) * 100
        percent_change_24h = float(data['result']['change24h']) * 100

        futures_response = requests.get(f"https://ftx.com/api/futures/{ticker}-PERP/stats")
        futures_data = json.loads(futures_response.content)
        next_funding_rate_percent = float(futures_data['result']['nextFundingRate']) * 100

        if percent_change_1h < 0:
            embed_color = 0xff0000
        elif percent_change_1h > 0:
            embed_color = 0x00ff00
        else:
            embed_color = 0xc6c6c6


        embed = discord.Embed(title=f'FTX Quickprice', color=embed_color)
        embed.add_field(name='Ticker:', value=ticker.upper())
        embed.add_field(name='Last Price:', value=f"{round(price, 5)} USD")
        embed.add_field(name='Volume:', value=f"{round(parseLargeValues(volume_24h)[0], 3)} {parseLargeValues(volume_24h)[1]} USD")
        embed.add_field(name='Next Funding Rate:', value=f"{round(next_funding_rate_percent, 5)}%")
        embed.add_field(name='1 Hour Change:', value=f"{round(percent_change_1h, 3)}%")
        embed.add_field(name='24 Hour Change:', value=f"{round(percent_change_24h, 3)}%")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='lendingprofit', description='Get lending profits.')
    @app_commands.describe(hours="Time range to calculate lending profit from.")
    async def lendingprofit(self, interaction: discord.Interaction, hours: int = None):
        embed = discord.Embed(title=f'FTX Lending Profit', color=0x00ff00)

        if hours:
            embed.add_field(name='Last: ', value=f'{hours} Hours')
            start_time = int(time.time() - (int(hours) * 60 * 60))
        else:
            embed.add_field(name='Last: ', value='All Lending Payments')
            start_time = 0

        lending_history = get('spot_margin/lending_history', { 'start_time': start_time, 'end_time': time.time() })        

        if lending_history['id'] == 'ERROR':
            await interaction.response.send_message(embed=createErrorEmbed(lending_history['data']))
        else:
            lending_history = lending_history['data']

            total = 0

            for entry in lending_history:
                total += entry['feeUsd']

            embed.add_field(name="Profit: ", value=f"${round(total, 2)} USD")

            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='fundingpayments', description='Get total funding payments.')
    @app_commands.describe(hours="Time range to calculate funding payments from.")
    async def fundingpayments(self, interaction: discord.Interaction, hours: int = None):
        embed = discord.Embed(title=f'FTX Perpetual Funding Payments', color=0x00ff00)

        if hours:
            embed.add_field(name='Last: ', value=f'{hours} Hours')
            start_time = int(time.time() - (int(hours) * 60 * 60))
        else:
            embed.add_field(name='Last: ', value='All Payments')
            start_time = 0

        funding_history = get('funding_payments', { 'start_time': start_time, 'end_time': time.time() })
        
        if funding_history['id'] == 'ERROR':
            await interaction.response.send_message(embed=createErrorEmbed(funding_history['data']))
        else:
            funding_history = funding_history['data']

            total = 0

            for entry in funding_history:
                total += entry['payment']

            if (total > 0):
                embed.add_field(name="Paid: ", value=f"${round(total, 2)} USD")
            elif (total < 0):
                embed.add_field(name="Received: ", value=f"${round(total * -1, 2)} USD")
            else:
                embed.add_field(name="Change:", value="None")

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='lendinfo', description='Lending Offer Information')
    async def lendinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'FTX Lending Offer Information', color=0x00ff00)

        lending_offers = get('spot_margin/offers')
            
        if lending_offers['id'] == 'ERROR':
            await interaction.response.send_message(embed=createErrorEmbed(lending_offers['data']))
        else:
            lending_offers = lending_offers['data']

            for lending_offer in lending_offers:
                if lending_offer['size'] != 0:
                    embed.add_field(name='Coin:', value=lending_offer['coin'], inline=True)
                    embed.add_field(name='Size:', value=f"{round(lending_offer['size'], 2)} {lending_offer['coin']}", inline=True)
                    embed.add_field(name='Minimum Rate:', value=f"{round((lending_offer['rate'] * 24 * 365 * 100), 3)}%", inline=True)
            
            if len(embed.fields) == 0:
                embed.add_field(name='Alert:', value='No active lending offers.')

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='stakeinfo', description='Stake information.')
    async def stakeinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f'FTX Stake Information', color=0x00ff00)

        stake_info = get('staking/balances')
            
        if stake_info['id'] == 'ERROR':
            await interaction.response.send_message(embed=createErrorEmbed(stake_info['data']))
        else:
            stake_info = stake_info['data']

            for stake_bal in stake_info:
                if stake_bal['staked'] != 0:
                    embed.add_field(name='Coin: ', value=stake_bal['coin'], inline=True)
                    embed.add_field(name='Staked: ', value=f"{round(stake_bal['staked'], 3)} {stake_bal['coin']}", inline=True)
                    embed.add_field(name='Lifetime Rewards:', value=f"{round(stake_bal['lifetimeRewards'], 3)} {stake_bal['coin']}", inline=True)
            
            if len(embed.fields) == 0:
                embed.add_field(name='Alert:', value='No assets currently staked.')

            await interaction.response.send_message(embed=embed)


# Setup & Link
async def setup(client: Bot):
    await client.add_cog(FTX(client))
