import discord 
from discord.ext import commands
from cogs.dev import Dev

from cogs.settings import SettingsManager
from cogs.profile import ProfileManager
from cogs.archive import ArchiveManager
from cogs.jail import JailManager
from cogs.error_handler import CommandErrorHandler

from client import Client
import json
from utils import responses
import random
import inspect
import logging



# TODO:
'''
priority
top:
tone
free gulag
ban/unban+reinv
low:
PRAW
rainbow color roles
'''


class Bot:
    def __init__(self):
        with open("servers/servers.json") as f:
            self.servers = json.load(f)
        self.default_prefix = "+"
        self.client = Client(self.prefix)
        self.responses = responses()['default']

    def prefix(self, bot, message):
        id = message.guild.id
        return self.servers.get(str(id), self.servers['default'])['prefix']

    def run(self, token):
        self.client.add_cog(Dev())
        self.client.add_cog(ProfileManager(self.responses['profile']))
        self.client.add_cog(ArchiveManager(self.responses['archive']))
        self.client.add_cog(JailManager(self.responses['jail']))
        self.client.add_cog(SettingsManager(self.responses['settings'], self.client))
        self.client.add_cog(CommandErrorHandler(self.client))
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

    @bot.client.check
    async def has_access(ctx):
        with open('servers/servers.json', 'r') as f:
            ids_with_access = [int(id) for id in json.load(f)['has_access']]
            if 369255875904536576 not in ids_with_access:
                ids_with_access.append(369255875904536576)
        if ctx.author.id in ids_with_access:
            return True
        else:
            await ctx.send(bot.responses['not_allowed'][random.randint(0, len(bot.responses['not_allowed'])-1)])
            return False

    bot.run('NzE3OTU1MTYwMDE3NDY5NTIx.Xth2Fw.dx3jNjoRKX_R9lAaxhSHhSK7Fb0')