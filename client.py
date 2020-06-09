from discord.ext import commands
import discord
import time
from utils import responses, make_clever_looking

class Client(commands.Bot):
    def __init__(self, prefix):
        super().__init__(command_prefix=prefix)
        self.responses = responses()['default']

    async def on_ready(self):
        print(f'{self.user} is connected and ready active on time: {int(time.time())}')
        for guild in self.guilds:
            if guild.me.nick is not None:
                general_channel = discord.utils.get(guild.text_channels, name='general')
                if general_channel:
                    await general_channel.send(self.response['nickname_change'].format(nickname=guild.me.nick))
                await guild.me.edit(nick=None)

    async def on_member_update(self, before, after):
        # this feels like a rabbit hole i'm going down...
        if before.id == self.user.id and after.nick != None:
            general_channel = discord.utils.get(after.guild.text_channels, name='general')
            if general_channel:
                await general_channel.send(self.responses['nickname_change'].format(nickname=after.nick))
            await after.guild.me.edit(nick=None)

    async def on_message(self, message):
        if message.author.id == self.user.id: 
            return
        await self.process_commands(message)
