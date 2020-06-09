from discord.ext import commands
import discord
import json
from inspect import stack
from utils import make_clever_looking, responses

class ArchiveManager(commands.Cog):    
    def __init__(self, responses):
        super().__init__()
        self.responses = responses

    
    @commands.command()
    async def reopen(self, ctx, channel: discord.TextChannel, *category_name):
        category_name = ' '.join(category_name).lower()
        category = discord.utils.find(lambda c: c.name.lower() == category_name, ctx.guild.categories)
        if category is not None:
            if channel.topic.startswith('Archived:') or channel.topic.startswith('Archived'):
                topic = channel.topic.replace('Archived:', '')
            else:
                topic = channel.topic
            # allow view message perms to @everyone role
            await channel.edit(category=category, topic=topic, overwrites={ctx.guild.default_role: discord.PermissionOverwrite()})
            await ctx.send(self.responses[stack()[0][3]]['success'].format(name=make_clever_looking(channel.name), category_name=make_clever_looking(category.name)))
        else:
            await ctx.send(self.responses[stack()[0][3]]['fail'].format(category_name=make_clever_looking(category_name)))

    @commands.command()
    async def archive(self, ctx, channel: discord.TextChannel, *category_name):
        category_name = ' '.join(category_name).lower()
        category = discord.utils.find(lambda c: c.name.lower() == category_name, ctx.guild.categories)
        if category is not None:
            if channel.topic:
                if channel.topic.startswith('Archived'):
                    topic = channel.topic
                else:
                    topic = f'Archived: {channel.topic}'
            else:
                topic = 'Archived'
            # delete any pre-existing channel overwrite perms
            changed_roles = channel.changed_roles
            for changed_role in changed_roles:
                await channel.set_permissions(changed_role, overwrite=None)
            # deny view message perms to @everyone role
            perm_overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }
            await channel.edit(category=category, topic=topic, overwrites=perm_overwrites)
            await ctx.send(self.responses[stack()[0][3]]['success'].format(name=make_clever_looking(channel.name), category_name=make_clever_looking(category.name)))
        else:
            await ctx.send(self.responses[stack()[0][3]]['fail'].format(category_name=make_clever_looking(category_name)))
