from discord.ext import commands
import discord
import json
from utils import format, get_servers_data, set_servers_data, guild_exists, update_setting
from checks import Checks
import random

class Permissions(commands.Cog):
    def __init__(self):
        self.update_response()
        
    def update_response(self):
        with open("info/responses.json", "r") as f:
            self.responses = json.load(f)

    @Checks.permissions_check()
    @commands.command(aliases=['setpermissiontype', 'set_permission', 'set_permissions', 'set_perm', 'set_perms'])
    async def set_permission_type(self, ctx, new_permission_type: str):
        self.update_response()
        responses = self.responses['permissions']['set_permission_type']

        data = get_servers_data()
        guild_id = str(ctx.guild.id)
        guild_exists(guild_id)
        permission_type = data[guild_id]["permission_type"]

        if new_permission_type.lower() in ["administrator", "admin"]:
            new_permission_type = "administrator"
        elif new_permission_type.lower() in ["manage_server", "server", "manage"]:
            new_permission_type = "manage_server"
        elif new_permission_type.lower() in ["everyone", "every"]:
            new_permission_type = "everyone"
        elif new_permission_type.lower() in ["custom"]:
            new_permission_type = "custom"
        else:
            print(f"error to be implemented: {new_permission_type} is not a permission type")
            return False

        if permission_type != new_permission_type:
            if permission_type == 'custom':
                update_setting(guild_id, 'custom_has_permission', [])
            update_setting(guild_id, 'permission_type', new_permission_type)
            message = responses['success'].format(permission_type=format(permission_type, "single_code"), new_permission_type=format(new_permission_type, "single_code"))
        else:
            message = responses['fail'].format(new_permission_type=format(new_permission_type, "single_code"))

        await ctx.send(message)

    @set_permission_type.error
    async def set_permission_type_error(self, ctx, error):
        responses = self.responses['permissions']['set_permission_type']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = responses['missing_permission_type']

        await ctx.send(embed=embed)

    
    @commands.command(aliases=['permissiontype', 'perm_type', 'type', 'server_permission', 'perms'])
    async def permission_type(self, ctx):
        self.update_response()
        responses = self.responses['permissions']['permission_type']

        data = get_servers_data()
        guild_id = str(ctx.guild.id)
        guild_exists(guild_id)
        permission_type = data[guild_id]["permission_type"]

        embed = discord.Embed()
        embed.color = random.randint(0, 16777215)
        content = None
        
        embed.title = responses["embed_data"]["title"].format(server=ctx.guild.name)
        embed.description = responses["embed_data"]["description"]

        embed.add_field(name=f"Permission type:", value=permission_type)

        if permission_type == "custom":
            user_ids = data[guild_id]['custom_has_permission']
            users = []
            for user_id in user_ids:
                user_obj = discord.utils.get(ctx.guild.members, id=user_id)
                users.append(f"{user_obj.name}#{user_obj.discriminator}")
            users.append(f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator} (server owner)")
            embed.add_field(name="Custom permission access", value=', '.join(users))

        await ctx.send(content=content, embed=embed)



    @Checks.permissions_check()
    @Checks.custom_permissions_enabled_check() # weeeee chaining decorators is funnnn
    @commands.command(aliases=['allowpermission', 'promote', 'allow_perm', 'allow_perms', 'add_perm', 'add_perms'])
    async def allow_permission(self, ctx, *users: discord.Member):
        self.update_response()
        responses = self.responses['permissions']['allow_permission']
        if not users:
            return await ctx.send(responses['no_users'])
        data = get_servers_data()
        guild_id = str(ctx.guild.id)
        message = ""
        user_names = []
        for user in users:
            user_id = int(user.id)
            if user_id not in data[guild_id]['custom_has_permission']:
                data[guild_id]['custom_has_permission'].append(user_id)
                user_names.append(user.name)
            else:
                message += f"{responses['fail'].format(user=user.name)}\n"
        set_servers_data(data)
        if user_names:
            user_names = ', '.join(user_names)
            message += responses['success'].format(users=user_names)
        await ctx.send(message)

        
    @Checks.permissions_check()
    @Checks.custom_permissions_enabled_check()
    @commands.command(aliases=['demote', 'remove_perm', 'remove_perms'])
    async def remove_permission(self, ctx, *users: discord.Member):
        # a literal copy and paste of allow_permission but with like 3 changes
        self.update_response()
        responses = self.responses['permissions']['remove_permission']
        if not users:
            return await ctx.send(responses['no_users'])
        data = get_servers_data()
        guild_id = str(ctx.guild.id)
        message = ""
        user_names = []
        for user in users:
            user_id = int(user.id)
            if user_id in data[guild_id]['custom_has_permission']:
                data[guild_id]['custom_has_permission'].remove(user_id)
                user_names.append(user.name)
            else:
                message += f"{responses['fail'].format(user=user.name)}\n"
        set_servers_data(data)
        if user_names:
            user_names = ', '.join(user_names)
            message += responses['success'].format(users=user_names)
        await ctx.send(message)