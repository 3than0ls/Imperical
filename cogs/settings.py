from discord.ext import commands
import discord
import json
from utils import embed_template, format, get_servers_data, update_setting, guild_exists
from checks import Checks
import random

class Settings(commands.Cog):
    def __init__(self, client):
        self.update_response()
        self.client = client

    def update_response(self):
        with open("info/responses.json", "r") as f:
            self.responses = json.load(f)

    # list people with access and list profiles

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Ping is {int(self.client.latency*1000)}ms')


    @Checks.permissions_check()
    @commands.command(aliases=['prefix', 'setprefix'])
    async def set_prefix(self, ctx, new_prefix: str):
        self.update_response()
        responses = self.responses['settings']['set_prefix']
        guild_exists(str(ctx.guild.id))
        if ctx.prefix != new_prefix:
            update_setting(str(ctx.guild.id), 'prefix', new_prefix)
            self.client.command_prefix = new_prefix
            await ctx.send(responses['success'].format(prefix=format(ctx.prefix, "single_code"), new_prefix=format(new_prefix, "single_code")))
        else:
            raise commands.BadArgument(new_prefix, "invalid_new_prefix")

    
    @commands.command(aliases=['server', 'config', 'serverconfig', 'settings'])
    async def server_config(self, ctx):
        self.update_response()
        responses = self.responses['settings']['server_config']
        guild_exists(str(ctx.guild.id))
        guild_id = str(ctx.guild.id)
        guild_data = get_servers_data()[guild_id]

        prefix = ctx.prefix
        number_of_profiles = len(guild_data["profiles"])
        permission_type = guild_data["permission_type"]

        jail_role = discord.utils.get(ctx.guild.roles, id=guild_data["jail_role"])
        jail_role = jail_role.mention if jail_role is not None else jail_role
        jail_channel = discord.utils.get(ctx.guild.text_channels, id=guild_data["jail_channel"])
        jail_channel = jail_channel.mention if jail_channel is not None else jail_channel

        embed = embed_template(
            title = responses["embed_data"]["title"].format(server=ctx.guild.name),
            description = responses["embed_data"]["description"]
        )
        

        embed.add_field(name="Bot prefix", value=f'`{prefix}`', inline=True)
        embed.add_field(name="Number of profiles", value=number_of_profiles, inline=True)
        embed.add_field(name="Permission type", value=permission_type, inline=True)
        if permission_type == "custom":
            user_ids = guild_data['custom_has_permission']
            users = []
            for user_id in user_ids:
                user_obj = discord.utils.get(ctx.guild.members, id=user_id)
                users.append(f"{user_obj.name}#{user_obj.discriminator}")
            users.append(f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator} (server owner)")
            embed.add_field(name="Custom permission access", value=', '.join(users))
        embed.add_field(name="Jail role", value=jail_role)
        embed.add_field(name="Jail channel", value=jail_channel)

        await ctx.send(content=None, embed=embed)


    
