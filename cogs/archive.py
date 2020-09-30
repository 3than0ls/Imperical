from discord.ext import commands
import discord
import json
from checks import Checks

class Archive(commands.Cog):    
    def __init__(self):
        self.update_response()

    def update_response(self):
        with open("info/responses.json", "r") as f:
            self.responses = json.load(f)

    @Checks.permissions_check()
    @commands.command(aliases=['open'])
    async def reopen(self, ctx, channel: discord.TextChannel, *category_name: str):
        self.update_response()
        responses = self.responses['archive']['reopen']

        if category_name:
            category_name = ' '.join(category_name).lower()
            category = discord.utils.find(lambda c: c.name.lower() == category_name, ctx.guild.categories)
            if category is None:
                raise commands.BadArgument(category_name, "invalid_category_name")
        else:
            category = None


        if channel.topic and channel.topic.startswith('Archived'):
            topic = channel.topic.replace('Archived:', '')
        else:
            topic = channel.topic

        await channel.edit(category=category, topic=topic, overwrites={ctx.guild.default_role: discord.PermissionOverwrite()})
        # allow view message perms to @everyone role and move it to given category

        await ctx.send(responses['success'].format(channel=channel.mention))

    @Checks.permissions_check()
    @commands.command(aliases=['hide'])
    async def archive(self, ctx, channel: discord.TextChannel, *category_name):
        self.update_response()
        responses = self.responses['archive']['archive']

        if category_name:
            category_name = ' '.join(category_name).lower()
            category = discord.utils.find(lambda c: c.name.lower() == category_name, ctx.guild.categories)
            if category is None:
                raise commands.BadArgument(category_name, "invalid_category_name")
        else:
            category = None

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

        await ctx.send(responses['success'].format(channel=channel.mention, category_name=category.name))