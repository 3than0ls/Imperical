from discord.ext import commands
import discord
import json
from utils import format, get_servers_data, guild_exists

import random

class Help(commands.Cog):
    def __init__(self, client):
        self.update_response()
        self.client = client

    def update_response(self):
        with open("info/responses.json", "r") as f:
            self.responses = json.load(f)
        with open("info/commands.json", "r") as f:
            self.info_commands = json.load(f)

    def help_embed(self, ctx, embed):
        response = self.responses["help"]["help"]
        prefix = get_servers_data()[str(ctx.guild.id)]['prefix']

        embed.title = response["embed_data"]["title"].format(name=ctx.me.name)
        embed.description = response["embed_data"]["description"].format(prefix=prefix)

            
        for cog in self.client.cogs.values(): # maybe change into .items() depending on needs
            name = cog.qualified_name.lower()
            if name in self.info_commands: # if the value exists -> add a field
                if self.info_commands[name]: # if the value is not an empty string -> add string as description field
                    embed.add_field(name=cog.qualified_name, value=self.info_commands[name]['_description'])
                else: # else add default _unknown string as description field
                    embed.add_field(name=cog.qualified_name, value=self.info_commands["_unknown"].format(item=cog.qualified_name))
            else: # print an error
                print(f"error: could not find cog {cog.qualified_name} in commands.json")
        
        return response.get("content")

    def module_help_embed(self, ctx, cog, embed):
        response = self.responses["help"]["modules"]
        prefix = get_servers_data()[str(ctx.guild.id)]['prefix']

        embed.title = response["embed_data"]["title"].format(module=cog.qualified_name)
        if cog.qualified_name.lower() in self.info_commands: # check if cog exists in info commands (this is not checking if command exists)
            info_command = self.info_commands[cog.qualified_name.lower()]
            embed.description = response["embed_data"]["description"].format(module=cog.qualified_name, prefix=prefix)
            for command in cog.get_commands():
                # similar to what happens in function help_embed above
                name = command.name.lower()
                if name in info_command:
                    if info_command[name]:
                        # give description a max length of 150 characters while viewing it in module help
                        description = info_command[name]['description'][0:150]+"..." if len(info_command[name]['description']) >= 150 else info_command[name]['description']
                        embed.add_field(name=command.name, value=description)
                    else: 
                        embed.add_field(name=command.name, value=self.info_commands["_unknown"].format(item=cog.qualified_name))
                else:
                    print(f"error: could not find command {command.name} in commands.json")
        else:
            embed.description = self.info_commands["_unknown"].format(item=cog.qualified_name)

        return response.get("content")

    def command_help_embed(self, command, embed):
        cog_name = command.cog.qualified_name.lower()
        response = self.responses["help"]["commands"]

        embed.title = response["embed_data"]["title"].format(command=command.name)

        if command.name.lower() in self.info_commands[cog_name]:
            info_command = self.info_commands[cog_name][command.name.lower()]
            embed.description = info_command['description']
            if "parameters" in info_command and len(info_command["parameters"]) > 0:
                params = [format(param[0], "single_code") for param in info_command["parameters"]]
                
                embed.add_field(name=f"\n{format('Parameters:', 'bold')}", value=', '.join(params), inline=False) # perhaps make this part how to use (ex: +help [specific])

                for parameter in info_command["parameters"]:
                    embed.add_field(name=format(parameter[0], "single_code"), value=parameter[1])
        else:
            embed.description = self.info_commands["_unknown"].format(item=command.name)

        command_aliases = [format(alias, "single_code") for alias in command.aliases]
        embed.add_field(name=format("Aliases: ", "bold"), value=', '.join(command_aliases), inline=False)

        return response.get("content")

    @commands.command(aliases=["info", 'commands'])
    async def help(self, ctx, specific=None):
        self.update_response()
        guild_exists(str(ctx.guild.id))

        if specific is not None:
            specific = specific.lower()
        
        embed = discord.Embed()
        embed.color = random.randint(0, 16777215)
        content = None

        # dictionary of lower cog name: cog
        cogs = {cog.qualified_name.lower(): cog for cog in self.client.cogs.values()}

        # dictionary of all lower command name: command
        # commands = {command.name.lower(): command for cog in self.client.cogs.values() for command in cog.get_commands() } # have to include command aliases
        commands = {}
        for cog in self.client.cogs.values():
            for command in cog.get_commands():
                commands[command.name.lower()] = command
                for alias in command.aliases:
                    commands[alias.lower()] = command

        if specific is None:
            content = self.help_embed(ctx, embed)
        elif specific in cogs:
            content = self.module_help_embed(ctx, cogs[specific], embed)
        elif specific in commands:
            self.command_help_embed(commands[specific], embed)
        else:
            # print(f"{specific} not found")
            self.help_embed(ctx, embed)
            content = f"Specific command or module \"{specific}\" was not found. Here is the main help page."


        await ctx.send(content=content, embed=embed)


