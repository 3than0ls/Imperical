from discord.ext import commands
import discord
import json
from utils import format, get_servers_data, set_servers_data, guild_exists
from checks import Checks

class Jail(commands.Cog):   
    def __init__(self):
        self.update_response() 

    def update_response(self):
        with open("info/responses.json", "r") as f:
            self.responses = json.load(f)
    

    @Checks.permissions_check()
    @commands.command(aliases=['create_gulag', 'create_prison', 'make_jail'])
    async def create_jail(self, ctx, jail_role: discord.Role, jail_channel: discord.TextChannel):
        self.update_response()
        responses = self.responses['jail']['create_jail']
        await ctx.send(responses['starting'])
        guild_id = str(ctx.guild.id)
        data = get_servers_data()
        # FIXME: if new channels are created after a jail role has been created, the role will have permissions to access it (assuming channel @everyone is open to everyone)
        channels = ctx.guild.channels    
        for channel in channels:
            if channel.id == jail_channel.id:
                await channel.set_permissions(jail_role, read_messages=True, send_messages=True)
            else:
                await channel.set_permissions(jail_role, read_messages=False)
        guild_id = str(ctx.guild.id)
        data = get_servers_data()
        data[guild_id]['jail_role'] = jail_role.id
        data[guild_id]['jail_channel'] = jail_channel.id
        set_servers_data(data)
            
        await ctx.send(responses['success'].format(jail_role=jail_role.mention, jail_channel=jail_channel.mention))

    @create_jail.error
    async def create_jail_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CheckFailure):
            return
        responses = self.responses['jail']['create_jail']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'jail_role':
                embed.description = responses['missing_role']
            elif error.param.name == 'jail_channel':
                embed.description = responses['missing_channel']
        elif isinstance(error, discord.Forbidden):
            embed.description = responses['forbidden']
            
        await ctx.send(embed=embed)


    @Checks.jail_exists_check()
    @Checks.permissions_check()
    @commands.command(aliases=['gulag', 'prison', 'imprison'])
    async def jail(self, ctx, *members: discord.Member):
        self.update_response()
        responses = self.responses['jail']['jail']

        if not members:
            return await ctx.send(responses["no_users"])

        guild_id = str(ctx.guild.id)
        guild_data = get_servers_data()[guild_id]

        jail_role = discord.utils.get(ctx.guild.roles, id=guild_data["jail_role"])
        jail_channel = discord.utils.get(ctx.guild.text_channels, id=guild_data["jail_channel"])

        for member in members:
            member_roles = [role for role in member.roles if role.name != '@everyone']
            if jail_role not in member_roles:
                await member.add_roles(jail_role)
            await member.remove_roles(*member_roles)
        names = [f"{member.mention}" for member in members]
        await ctx.send(responses["success"].format(names=', '.join(names)))

    @jail.error
    async def jail_error(self, ctx, error):
        responses = self.responses['jail']['jail']['error']
        error = getattr(error, 'original', error)
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, discord.Forbidden):
            embed.description = responses['forbidden']
            
        await ctx.send(embed=embed)


    @Checks.jail_exists_check()
    @Checks.permissions_check()
    @commands.command(aliases=['destroy_jail', 'free_jail', 'reset_jail'])
    async def delete_jail(self, ctx):
        self.update_response()
        responses = self.responses['jail']['delete_jail']
        guild_id = str(ctx.guild.id)
        data = get_servers_data()
        jail_role = discord.utils.get(ctx.guild.roles, id=data[guild_id]["jail_role"])
        await ctx.send(responses["starting"].format(jail_role=jail_role.name))
        channels = ctx.guild.channels
        for channel in channels:
            await channel.set_permissions(jail_role, overwrite=None)
        data[guild_id]["jail_role"] = None
        data[guild_id]["jail_channel"] = None
        set_servers_data(data)
        await ctx.send(responses["success"].format(jail_role=jail_role.mention))

    @delete_jail.error
    async def delete_jail_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CheckFailure):
            return
        responses = self.responses['jail']['delete_jail']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, discord.Forbidden):
            embed.description = responses['forbidden']
            
        await ctx.send(embed=embed)