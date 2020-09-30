from utils import embed_template, get_responses, format
import discord
from discord.ext import commands

class CommandErrorHandler(commands.Cog, command_attrs=dict(hidden=True)):       
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception
        
        edited from https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        """
        # if hasattr(ctx.command, 'on_error'):
        #    return
        
        ignored = (commands.CommandNotFound, commands.CheckFailure)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return
        
        elif isinstance(error, KeyError):
            command = self.client.get_command(ctx.invoked_with)
            responses = get_responses()[command.cog.qualified_name.lower()][command.name]
            embed = embed_template(title="An internal responder message error has occured", description=f"Missing responder `{error.args[0]}` for command `command.name`")
            embed.color = 15138816
            return await ctx.send(content=None, embed=embed)
        else:
            try:
                command = self.client.get_command(ctx.invoked_with)
                responses = get_responses()[command.cog.qualified_name.lower()][command.name]

                message = ""
                if isinstance(error, commands.MissingRequiredArgument):
                    message = responses["error"][f"missing_{error.param.name}"]
                    
                elif isinstance(error, commands.BadArgument):
                    if len(error.args) == 1:
                        message = responses["error"][error.args[0]]
                    elif len(error.args) == 2:
                        message = responses["error"][error.args[1]].format(profile=format(error.args[0], 'single_code'))

                elif isinstance(error, discord.Forbidden):
                    message = responses["error"]['forbidden']
                
                embed = embed_template(title="An error has occured", description=message)
                embed.color = 15138816
                return await ctx.send(content=None, embed=embed)
            except KeyError:
                command = self.client.get_command(ctx.invoked_with)
                responses = get_responses()[command.cog.qualified_name.lower()][command.name]
                embed = embed_template(title="An internal responder message error has occured", description=f"Missing responder `{error.args[0]}` for command `command.name`")
                embed.color = 15138816
                return await ctx.send(content=None, embed=embed)
