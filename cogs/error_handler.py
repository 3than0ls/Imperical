import traceback
import sys
from discord.ext import commands
import discord
from utils import make_clever_looking

class CommandErrorHandler(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception
        
        edited from https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        """

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound, commands.CheckFailure)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')
            
        await ctx.send(make_clever_looking(error))