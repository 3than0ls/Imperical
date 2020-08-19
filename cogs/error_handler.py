import traceback
import sys
from discord.ext import commands
import discord
from utils import format
import json

class CommandErrorHandler(commands.Cog, command_attrs=dict(hidden=True)):       
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
            
            
        raise error