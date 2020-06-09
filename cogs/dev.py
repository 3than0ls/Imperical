from discord.ext import commands
import discord
from utils import make_smart_looking, filter_dunders, make_clever_looking

class Dev(commands.Cog):

    @commands.command()
    async def get_user_id(self, ctx, member: discord.Member = None):
        if not member: member = ctx.author
        await ctx.send(f'User {member.name} has an ID of {make_clever_looking(member.id)}')


    @commands.command(aliases=['roles'])
    async def user_roles(self, ctx, member: discord.Member = None):
        if not member: member = ctx.author
        roles = [role.id for role in filter(lambda r: r.name != '@everyone', member.roles)]
        await ctx.send(make_smart_looking(roles))

    @commands.command()
    async def perms_for(self, ctx, member: discord.Member = None):
        if not member: member = ctx.author
        await ctx.send(make_smart_looking(dir(ctx.channel.permissions_for(member))))

    @commands.command()
    async def get_role_id(self, ctx, role: discord.Role = None):
        if role:
            await ctx.send(f'Role {role.name} has an ID of {make_clever_looking(role.id)}')
        else:
            await ctx.send(f'Missing argument {make_clever_looking("role")}')

    @commands.command()
    async def dir(self, ctx, arg=None):
        info = ctx
        if arg:
            parts = arg.split('.')
            for arg in parts:
                try:
                    info = getattr(info, arg)
                except AttributeError:
                    await ctx.send(f'{arg} is not an attribute of {info}')
            else:
                try:
                    await ctx.send(make_smart_looking(filter_dunders(dir(info))))
                except discord.errors.HTTPException:
                    await ctx.send('In content: Must be 2000 or fewer in length.')
        else:
            await ctx.send(make_smart_looking(filter_dunders(dir(info))))

    @commands.command()
    async def info(self, ctx, arg=None):
        info = ctx
        if arg:
            parts = arg.split('.')
            for arg in parts:
                try:
                    info = getattr(info, arg)
                except AttributeError:
                    await ctx.send(f'{arg} is not an attribute of {info}')
                    break
            else:
                await ctx.send(make_smart_looking(info))

        else:
            await ctx.send(make_smart_looking(info))