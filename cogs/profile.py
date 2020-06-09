from discord.ext import commands
import discord
import json
from copy import deepcopy
from inspect import stack
import typing
from utils import make_smart_looking, make_clever_looking


class ProfileManager(commands.Cog):
    def __init__(self, responses):
        self.profiles_path = 'servers/servers.json'
        self.responses = responses

    def get_profile(self, guild_id, profile):
        with open(self.profiles_path, 'r') as f:
            profiles = json.load(f)[str(guild_id)]['profiles']
            if profile in profiles:
                role_ids = profiles[profile]
                return role_ids
            else:
                return None

    def remove_profile_role(self, guild_id, role_id, profile):
        with open(self.profiles_path, 'r') as f:
            data = json.load(f)
        data[guild_id]['profiles'][profile].remove(role_id)
        with open(self.profiles_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    @commands.command(aliases=['profiles'])
    async def list_profiles(self, ctx):
        seperator = '\n------------------\n\n'
        response = ''
        with open('servers/servers.json', 'r') as f:
            profiles = json.load(f)[str(ctx.guild.id)]['profiles']
        for profile_name, profile in profiles.items():
            profile_data = f'{profile_name}:\n'
            for role_id in profile:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                profile_data += f'\t{role_id} (name: {"Role not found" if not hasattr(role, "name") else role.name})\n'
            response += f'{profile_data}{seperator}'
        response = response[:-len(seperator)]
        if len(response) <= 1985:
            await ctx.send(make_smart_looking(response))
        else:
            responses = response.split(seperator)
            for response in responses:
                await ctx.send(make_smart_looking(response))

    @commands.command(aliases=['server_profile'])
    async def profile_everyone(self, ctx, min_roles: typing.Optional[int] = 3):
        guild_id = str(ctx.guild.id)
        created_profiles = 0
        replaced_profiles = 0
        for member in ctx.guild.members:
            if len(member.roles) >= min_roles + 1 and not member.bot:
                # read server configs
                with open(self.profiles_path, 'r') as f:
                    data = json.load(f)
                    # if guild id and object doesn't exist in servers json list, define it
                    if guild_id not in data:
                        data[str(guild_id)] = deepcopy(data['default'])
                    profiles = data[guild_id]['profiles']
                name = member.name.lower()
                if name in profiles:
                    replaced_profiles += 1
                else:
                    created_profiles += 1
                roles = [role.id for role in member.roles if role.name != '@everyone']
                profiles[name] = list(set(roles))

                # write server configs
                with open(self.profiles_path, 'w') as f:
                    json.dump(data, f, indent=4)
        if created_profiles == 0:
            await ctx.send(self.responses[stack()[0][3]]['fail'])
        else:
            await ctx.send(self.responses[stack()[0][3]]['success'].format(created_amount=created_profiles, replaced_amount=replaced_profiles))

        
    @commands.command()
    async def create_profile(self, ctx, name: str, *role_sources: commands.Greedy[typing.Union[discord.Member, discord.Role]]):
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
        roles = [role.id for role in filter(lambda r: r.name != '@everyone', add_roles)]
        guild_id = str(ctx.guild.id)
            
        if roles:
            # read server configs
            with open(self.profiles_path, 'r') as f:
                data = json.load(f)
                # if guild id and object doesn't exist in servers json list, define it
                if guild_id not in data:
                    data[str(guild_id)] = deepcopy(data['default'])
                profiles = data[guild_id]['profiles']

            if name in profiles:
                await ctx.send(self.responses[stack()[0][3]]['replace'].format(name=make_clever_looking(name)))
            profiles[name] = roles

            # write server configs
            with open(self.profiles_path, 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.send(self.responses[stack()[0][3]]['success'].format(roles=make_clever_looking(roles), name=make_clever_looking(name)))
        else:
            await ctx.send(self.responses[stack()[0][3]]['fail'])

    @commands.command()
    async def delete_profile(self, ctx, profile: str):
        # read server configs
        with open(self.profiles_path, 'r') as f:
            data = json.load(f)
        guild_id = str(ctx.guild.id)
        if guild_id not in data:
            return await ctx.send(self.responses[stack()[0][3]]['fail'].format(profile=profile))
        profiles = data[guild_id]['profiles']
        if profile not in profiles:
            return await ctx.send(self.responses[stack()[0][3]]['fail'].format(profile=profile))
        del profiles[profile]

        # write server configs
        with open(self.profiles_path, 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send(self.responses[stack()[0][3]]['success'].format(profile=profile))

    @commands.command(aliases=['wipe_profiles'])
    async def clear_profiles(self, ctx):
        with open(self.profiles_path, 'r') as f:
            data = json.load(f)
        guild_id = str(ctx.guild.id)
        profiles = data[guild_id]['profiles']
        if not profiles:
            return await ctx.send(self.responses[stack()[0][3]]['fail'])
        profiles.clear()

        with open(self.profiles_path, 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send(self.responses[stack()[0][3]]['success'])

    
    @commands.command(aliases=['profile'])
    async def add_profile(self, ctx, profile: str, *members: discord.Member, clear_previous: bool=True):
        # make default member author
        role_ids = self.get_profile(str(ctx.guild.id), profile)
        if role_ids:
            roles = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in role_ids]
            amount = 0
            for member in members:
                # clear members previous roles
                if clear_previous:
                    member_roles = [role for role in member.roles if role.name != '@everyone']
                    await member.remove_roles(*member_roles)

                roles_to_be_added = []
                for i, role in enumerate(roles):
                    if role is not None:
                        if role not in member.roles:
                            roles_to_be_added.append(role)
                            amount += 1
                        # else:
                        #     await ctx.send(self.responses[stack()[0][3]]['skip'].format(name=member.name, role=make_clever_looking(role), profile=make_clever_looking(profile)))
                    else:
                        not_found_role_id = role_ids[i]
                        self.remove_profile_role(str(ctx.guild.id), int(not_found_role_id), profile)
                        await ctx.send(self.responses[stack()[0][3]]['remove'].format(not_found_role_id=make_clever_looking(not_found_role_id)))
                await member.add_roles(*roles_to_be_added)

            if len(members) == 1:  # only send if a profile was assigned to one member
                await ctx.send(self.responses[stack()[0][3]]['assigned_total'].format(amount=amount, name=member.name))
            await ctx.send(self.responses[stack()[0][3]]['success'])
        else:
            await ctx.send(self.responses[stack()[0][3]]['fail'].format(profile=make_clever_looking(profile)))

    
    @commands.command(aliases=['strip'])
    async def remove_profile(self, ctx, profile: str, *members: discord.Member):
        # make default member author
        role_ids = self.get_profile(str(ctx.guild.id), profile)
        if role_ids:
            roles = [discord.utils.get(ctx.guild.roles, id=role_id) for role_id in role_ids]
            amount = 0
            for member in members:
                roles_to_be_removed = []
                for i, role in enumerate(roles):
                    if role is not None:
                        if role in member.roles:
                            roles_to_be_removed.append(role)
                            amount += 1
                        # else:
                        #     await ctx.send(self.responses[self.tone]['remove_profile']['skip_remove'][0].format(name=member.name, role=make_clever_looking(role), profile=make_clever_looking(profile)))
                    else:
                        not_found_role_id = role_ids[i]
                        self.remove_profile_role(str(ctx.guild.id), int(not_found_role_id), profile)
                        await ctx.send(self.responses[stack()[0][3]]['remove_profile']['remove'].format(not_found_role_id=not_found_role_id))
                # remove all roles to be removed at once
                await member.remove_roles(*roles_to_be_removed)
            if len(members) == 1:  # only send if a profile was assigned to one member
                await ctx.send(self.responses[stack()[0][3]]['removed_total'].format(amount=amount, name=member.name))
            await ctx.send(self.responses[stack()[0][3]]['success'])
        else:
            await ctx.send(self.responses[stack()[0][3]]['not_found'].format(profile=make_clever_looking(profile)))