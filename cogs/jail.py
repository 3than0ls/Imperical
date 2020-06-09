from discord.ext import commands
import discord
import json
from utils import make_clever_looking, responses
from inspect import stack

class JailManager(commands.Cog):    
    def __init__(self, responses):
        super().__init__()
        self.responses = responses

    @commands.command()
    async def jail(self, ctx, jail_role: discord.Role, *members: discord.Member):
        for member in members:
            member_roles = [role for role in member.roles if role.name != '@everyone']
            await member.remove_roles(*member_roles)
            await member.add_roles(jail_role)
        names = [make_clever_looking(member.name) for member in members]
        await ctx.send(self.responses[stack()[0][3]]['success'].format(jail_role=make_clever_looking(jail_role.name), members=', '.join(names)))

    @commands.command(aliases=['destroy_jail', 'delete_jail'])
    async def free_jail(self, ctx, role: discord.Role):
        channels = ctx.guild.channels
        for channel in channels:
            await channel.set_permissions(role, overwrite=None)
        await ctx.send(self.responses[stack()[0][3]]['success'].format(name=make_clever_looking(role.name)))

    @commands.command(aliases=['create_gulag'])
    async def create_jail(self, ctx, role: discord.Role, jail_channel: discord.TextChannel):
        # if new channels are created after gulagify on a role, role will have permissions to access (assuming channel @everyone is open to everyone)
        channels = ctx.guild.channels
            
        for channel in channels:
            if channel.id == jail_channel.id:
                await channel.set_permissions(role, read_messages=True, send_messages=True)
            else:
                await channel.set_permissions(role, read_messages=False)
            
        await ctx.send(self.responses[stack()[0][3]]['success'].format(role_name=make_clever_looking(role.name), jail_channel=make_clever_looking(jail_channel)))