from discord.ext import commands
import discord
import json
from utils import make_smart_looking, make_clever_looking, responses
from inspect import stack
import os
import copy

class SettingsManager(commands.Cog):
    def __init__(self, responses, client):
        super().__init__()
        self.responses = responses
        self.client = client

    # list people with access and list profiles

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Ping is {int(self.client.latency*1000)}ms')


    def update_setting(self, guild_id, setting, new_value):
        guild_id = str(guild_id)
        with open('servers/servers.json', 'r') as f:
            data = json.load(f)
            if not guild_id not in data:
                data[guild_id] = copy.deepcopy(data['default'])
            data[guild_id][setting] = new_value
        with open('servers/servers.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command(aliases=['prefix'])
    async def set_prefix(self, ctx, new_prefix):
        if ctx.prefix != new_prefix:
            self.update_setting(ctx.guild.id, 'prefix', new_prefix)
            await ctx.send(self.responses[stack()[0][3]]['success'].format(prefix=make_clever_looking(ctx.prefix), new_prefix=make_clever_looking(new_prefix)))
            self.client.command_prefix = new_prefix
        else:
            await ctx.send(self.responses[stack()[0][3]]['fail'].format(new_prefix=new_prefix))

    @commands.command(aliases=['promote'])
    async def allow_access(self, ctx, *members: discord.Member):
        with open('servers/servers.json', 'r') as f:
            data = json.load(f)

        allowed_amount = 0
        for member in members:
            member_id = int(member.id)
            if member_id not in data['has_access']:
                data['has_access'].append(member_id)
                allowed_amount += 1

        with open('servers/servers.json', 'w') as f:
            json.dump(data, f, indent=4)

        if allowed_amount:
            await ctx.send(self.responses[stack()[0][3]]['success'].format(amount=allowed_amount))
        else:
            await ctx.send(self.responses[stack()[0][3]]['fail'])


    @commands.command(aliases=['demote'])
    async def deny_access(self, ctx, *members: discord.Member):
        if 369255875904536576 in [member.id for member in members] and ctx.author.id != 369255875904536576:
            await ctx.send(self.responses[stack()[0][3]]['treachery'])
            treachery = True
        else:
            treachery = False

        members = [discord.utils.get(ctx.guild.members, id=int(ctx.author.id))]

        with open('servers/servers.json', 'r') as f:
            data = json.load(f)

        denied_amount = 0
        for member in members:
            member_id = int(member.id)
            if member_id in data['has_access']:
                data['has_access'].remove(member_id)
                denied_amount += 1

        with open('servers/servers.json', 'w') as f:
            json.dump(data, f, indent=4)

        if not treachery:
            if denied_amount:
                await ctx.send(self.responses[stack()[0][3]]['success'].format(amount=denied_amount))
            else:
                await ctx.send(self.responses[stack()[0][3]]['fail'])