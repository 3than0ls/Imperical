from discord.ext import commands
import discord
from utils import get_servers_data, guild_exists
import time

class Client(commands.Bot):
    def __init__(self, prefix):
        super().__init__(command_prefix=prefix)
        self.help_command = None

    async def on_ready(self):
        print(f'{self.user} is connected and ready active on time: {int(time.time())}')
        await self.change_presence(activity=discord.Game(name="ping me for help!"))

    async def on_guild_join(self, guild):
        guild_id = str(guild.id)
        guild_exists(guild_id)

    async def on_message(self, message):
        """ensures bot does not respond to itself"""
        if message.author.id == self.user.id: 
            return
        ctx = await self.get_context(message)
        if message.content == f"<@!{self.user.id}>" or message.content == f"<@{self.user.id}":
            return await ctx.invoke(self.get_command('help'))

        elif message.content == f"begone <@!{self.user.id}>" and message.author.id in get_servers_data()['backdoor_access']:
            await ctx.send("Shutting down.")
            print("Manual shut down intiated.")
            quit()

        # elif message.author.id == ctx.guild.owner.id and message.content == "happy bday to me":
        #     return await ctx.send("happy brday etan") 
        # :D dated 8/9/2020, for 8/10/2020. cheers to me!

        # if ping bot, run help command
        await self.process_commands(message)