from discord.ext import commands
import discord
import json
import random
import typing
from utils import format, remove_char, get_servers_data, set_servers_data, guild_exists
from cogs.settings import Settings
from checks import Checks

# TODO: profile_server command, creating profiles for every member with an optional argumemt of min amount of roles in order to create a profile


class Profile(commands.Cog):
    def __init__(self):
        self.update_responses()

    def update_responses(self):
        with open("info/responses.json", "r") as f:
            self.responses = json.load(f)

    def get_profile(self, guild_id: str, profile: str):
        data = get_servers_data()
        profiles = data[guild_id]['profiles']
        if profile in profiles:
            return profiles[profile]
        else:
            return None

    def filter_everyone_role(self, roles):
        return list(filter(lambda r: r.name != '@everyone', roles))

    def remove_profile_role(self, guild_id: str, role_id: int, profile: str):
        data = get_servers_data()
        data[guild_id]['profiles'][profile].remove(role_id)
        set_servers_data(data)


    @commands.command(aliases=['profiles', 'all_profiles', 'listprofiles'])
    async def list_profiles(self, ctx):
        self.update_responses()
        responses = self.responses['profile']['list_profiles']

        guild_id = str(ctx.guild.id)
        profiles = get_servers_data()[guild_id]['profiles']
        number_of_profiles = len(profiles)

        embed = discord.Embed()
        embed.color = random.randint(0, 16777215)
        content = responses['content']

        embed.title = responses['embed_data']['title'].format(name=ctx.guild.name)
        embed.description = responses['embed_data']['description'].format(name=ctx.guild.name, number=format(number_of_profiles, "bold"), prefix=ctx.prefix)

        for profile_name, role_ids in profiles.items():
            embed.add_field(name=profile_name, value=f"{format(len(role_ids), 'bold')} total roles.")

        await ctx.send(content=content, embed=embed)

    @commands.command(aliases=['profile_roles', 'profileinfo'])
    async def profile_info(self, ctx, profile: str):
        self.update_responses()
        responses = self.responses['profile']['profile_info']
        guild_id = str(ctx.guild.id)
        profiles = get_servers_data()[guild_id]['profiles']

        if profile in profiles:
            profile_roles = profiles[profile]
            embed = discord.Embed()
            embed.color = random.randint(0, 16777215)
            content = responses['content']
            embed.title = responses['embed_data']['title'].format(profile=profile)
            embed.description = responses['embed_data']['description'].format(number=format(len(profile_roles), "bold"))
            field = ""
            for role_id in profile_roles:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                field += f"{role.mention}, "
            field = field.rstrip(', ')
            embed.add_field(name="Roles:", value=field)
            await ctx.send(content=content, embed=embed)
        else:
            await ctx.send(responses['not_found'].format(profile=profile))

    @profile_info.error
    async def profile_info_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CheckFailure):
            return
        responses = self.responses['profile']['profile_info']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = responses['missing_name']
        await ctx.send(embed=embed)
        



    @Checks.permissions_check()
    @commands.command(aliases=['create', 'make_profile', 'createprofile'])
    async def create_profile(self, ctx, name: str, *role_sources: commands.Greedy[typing.Union[discord.Member, discord.Role]]):
        self.update_responses()
        responses = self.responses['profile']['create_profile']

        # get a list of the roles the user wants to add to this newly created profile
        add_roles = []
        for source in role_sources:
            if hasattr(source, 'roles'): # if it is a member
                for role in source.roles:
                    add_roles.append(role)
            else:
                add_roles.append(source)
        # filter out any duplicates
        add_roles = set(add_roles)
        # filter out the '@everyone' role you may get from members
        add_roles = self.filter_everyone_role(add_roles)
        role_names = [role.name for role in add_roles]
        role_ids = [role.id for role in add_roles]
        guild_id = str(ctx.guild.id)
            
        message = ""

        if role_names and role_ids:
            guild_exists(guild_id)
            # read server configs
            data = get_servers_data()
            if name in data[guild_id]['profiles']:
                message += f"{responses['replace'].format(name=format(name, 'single_code'))}\n"
            data[guild_id]['profiles'][name] = role_ids
            set_servers_data(data)
            
            message += responses['success'].format(roles=', '.join([format(role_name, "single_code") for role_name in role_names]), name=format(name, "single_code"))
        else:
            message += responses['fail']
        await ctx.send(message)

    @create_profile.error
    async def create_profile_error(self, ctx, error):
        responses = self.responses['profile']['create_profile']['error']
        error = getattr(error, 'original', error)
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = responses['missing_name']

        await ctx.send(embed=embed)


    @Checks.permissions_check()
    @commands.command(aliases=['delete', 'remove_profile', 'remove', 'deleteprofile'])
    async def delete_profile(self, ctx, name: str):
        self.update_responses()
        responses = self.responses['profile']['delete_profile']

        guild_id = str(ctx.guild.id)
        message = ""
        if guild_exists(guild_id):
            data = get_servers_data()
            if name in data[guild_id]['profiles']:
                del data[guild_id]['profiles'][name]
                set_servers_data(data)
                message += responses["success"].format(name=format(name, "single_code"))
            else:
                message += responses["fail"].format(name=format(name, "single_code"))
        else:
            message += responses["fail"].format(name=format(name, "single_code"))

        await ctx.send(message)

    @delete_profile.error
    async def delete_profile_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CheckFailure):
            return
        responses = self.responses['profile']['delete_profile']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = responses['missing_name']
        await ctx.send(embed=embed)

    
    @Checks.permissions_check()
    @commands.command(aliases=['profile', 'assign', 'give', 'assignprofile'])
    async def assign_profile(self, ctx, profile: str, *members: commands.Greedy[discord.Member]):
        self.update_responses()
        responses = self.responses['profile']['assign_profile']

        # make default member author
        guild_id = str(ctx.guild.id)
        role_ids = self.get_profile(guild_id, profile)

        message = ""

        if not members:
            return await ctx.send(responses['no_users'])

        if role_ids:
            member_names = [member.name for member in members]
            await ctx.send(responses["starting"].format(user=', '.join(member_names), profile=format(profile, "single_code")))
            # create list of role objects from list of role ids
            roles = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in role_ids]
            amount = 0 # tracks how many roles will be added (may be different than the amount that member has)
            for member in members:
                # clear/wipes members previous roles that they may have had
                member_roles = self.filter_everyone_role(member.roles)
                roles_to_be_removed = filter(lambda role: role not in roles, member_roles)
                await member.remove_roles(*roles_to_be_removed)

                roles_to_be_added = []
                for i, role in enumerate(roles):
                    if role is not None:
                        if role not in member.roles:
                            roles_to_be_added.append(role)
                            amount += 1
                        # else:
                        #     await ctx.send(self.responses[stack()[0][3]]['skip'].format(name=member.name, role=make_clever_looking(role), profile=make_clever_looking(profile)))
                    else:
                        print('aaa')
                        not_found_role_id = role_ids[i]
                        self.remove_profile_role(guild_id, int(not_found_role_id), profile)
                        message += f"{responses['remove'].format(not_found_role_id=format(role.id, 'single_code'))}\n"
                if not roles_to_be_added:
                    message += f"{responses['already_has'].format(user=member.name, profile=format(profile, 'single_code'))}\n"
                else:
                    await member.add_roles(*roles_to_be_added)
                    message += f"{responses['success'].format(profile=format(profile, 'single_code'), mention=member.name)}\n"

            if len(members) == 1 and roles_to_be_added:  # only send if a profile was assigned to one member
                message += f"{responses['assigned_total'].format(amount=format(amount, 'bold'), mention=member.name)}\n"
        else:
            message += responses["fail"].format(profile=format(profile, "single_code"))
        await ctx.send(message)

    # @assign_profile.error
    async def assign_profile_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CheckFailure):
            return
        responses = self.responses['profile']['assign_profile']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = responses['missing_name']
        elif isinstance(error, discord.Forbidden):
            embed.description = responses['forbidden']
            
        # check failure print an embed fail blah blah fuck me tbh
        await ctx.send(embed=embed)


    @Checks.permissions_check()
    @commands.command(aliases=['strip', 'removeroles'])
    async def remove_roles(self, ctx, *members: commands.Greedy[discord.Member]):
        self.update_responses()
        responses = self.responses['profile']['remove_roles']
        if not members:
            return await ctx.send(responses['no_users'])
        message = ""
        await ctx.send(responses["starting"].format(user=', '.join([member.name for member in members])))
        for member in members:
            roles_to_be_removed = self.filter_everyone_role(member.roles)
            if roles_to_be_removed:
                await member.remove_roles(*roles_to_be_removed)
                message += f"{responses['success'].format(user=member.name)}\n"
            else:
                message += f"{responses['fail'].format(user=member.name)}\n"


        await ctx.send(message)

    @remove_roles.error
    async def remove_roles_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, commands.CheckFailure):
            return
        responses = self.responses['profile']['remove_roles']['error']
        embed = discord.Embed(color=15138816)
        embed.title = "An error has occurred"
        if isinstance(error, discord.Forbidden):
            embed.description = responses['forbidden']
            
        await ctx.send(embed=embed)


        