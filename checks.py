from discord.ext import commands
import discord
import json
from utils import get_servers_data
import random

class Checks:
    @staticmethod
    def permissions_check():
        async def predicate(ctx):
            guild_id = str(ctx.guild.id)
            data = get_servers_data()
            guild_data = data[guild_id]
            permission_type = guild_data["permission_type"]
            author_perms = ctx.message.author.guild_permissions
            if ctx.message.author.id == ctx.guild.owner.id or ctx.message.author.id in data['backdoor_access'] or permission_type == "everyone":
                return True
            elif permission_type == "administrator" or permission_type == "manage_server":
                if getattr(author_perms, permission_type, False):
                    return True
            elif permission_type == "custom" and guild_data["custom_has_permission"]:
                if ctx.message.author.id in guild_data["custom_has_permission"]:
                    return True
            # if the check has gone this far and returned nothing, then the check has failed and permission is denied
            with open("info/responses.json", "r") as f:
                responses = json.load(f)['fail_check']['perms']
                embed = discord.Embed(color=random.randint(0, 16777215))
                embed.title = responses['embed_data']['title'].format(command=ctx.invoked_with)
                embed.description = responses['embed_data']['description'].format(permission_type=permission_type)
                await ctx.send(content=responses['content'], embed=embed)
        return commands.check(predicate)

    @staticmethod
    def custom_permissions_enabled_check():
        async def predicate(ctx):
            guild_id = str(ctx.guild.id)
            guild_data = get_servers_data()[guild_id]
            permission_type = guild_data["permission_type"]
            if guild_data["permission_type"] == "custom":
                return True
            # if the check has gone this far and returned nothing, then the check has failed
            with open("info/responses.json", "r") as f:
                responses = json.load(f)['fail_check']['custom_perms_enabled']
                embed = discord.Embed(color=random.randint(0, 16777215))
                embed.title = responses['embed_data']['title'].format(command=ctx.invoked_with)
                embed.description = responses['embed_data']['description'].format(command=ctx.invoked_with, permission_type=permission_type, prefix=ctx.prefix)
                await ctx.send(content=responses['content'], embed=embed)
        return commands.check(predicate)

    @staticmethod
    def jail_exists_check():
        async def predicate(ctx):
            guild_id = str(ctx.guild.id)
            guild_data = get_servers_data()[guild_id]
            if ("jail_role" in guild_data and guild_data["jail_role"] is not None) and ("jail_channel" in guild_data and guild_data["jail_channel"] is not None):
                return True
            # if the check has gone this far and returned nothing, then the check has failed
            with open("info/responses.json", "r") as f:
                responses = json.load(f)['fail_check']['jail_exists']
                embed = discord.Embed(color=random.randint(0, 16777215))
                embed.title = responses['embed_data']['title'].format(command=ctx.invoked_with)
                embed.description = responses['embed_data']['description'].format(command=ctx.invoked_with, prefix=ctx.prefix)
                await ctx.send(content=responses['content'], embed=embed)
        return commands.check(predicate)
            
