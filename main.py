import discord 
from discord.ext import commands

from cogs.help import Help
from cogs.profile import Profile
from cogs.jail import Jail
from cogs.archive import Archive
from cogs.permissions import Permissions
from cogs.settings import Settings
from cogs.error_handler import CommandErrorHandler

from client import Client
import json
from utils import get_servers_data
import random
import inspect
import logging


# TODO: role/profile persist, reaction to get profile (maybe)


class Bot:
    def __init__(self):
        self.servers = get_servers_data()
        self.client = Client(self.prefix)

    def prefix(self, bot, message):
        id = message.guild.id
        return self.servers.get(str(id), self.servers['default'])['prefix']

    def run(self, token):
        self.client.add_cog(Settings(self.client))
        self.client.add_cog(Permissions())
        self.client.add_cog(Help(self.client))
        self.client.add_cog(Profile())
        self.client.add_cog(Jail())
        self.client.add_cog(Archive())
        self.client.add_cog(CommandErrorHandler())
        self.client.run(token)
        

if __name__ == '__main__':
    bot = Bot()

    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    @bot.client.check
    async def block_dms(ctx):
        return ctx.guild is not None

    bot.run('NzE3OTU1MTYwMDE3NDY5NTIx.Xt_N4g.yclT9JANhFdvHoSx9Gm4KhdjMWo')