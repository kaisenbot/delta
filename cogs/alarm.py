import discord
from discord.ext import commands

import asyncio

class alarm:
    def __init__(self,bot):
        self.bot = bot
        self.alert_list = {}
        self._queue = asyncio.Queue(loop=self.bot.loop)
    
    @commands.command(pass_context=True)
    async def run(self,ctx,*,line:str):
        print(self._queue)
        result = eval(line)
        if result is not None:
            return await self.bot.say(result)
    '''    
    @alerts.command(pass_context=True)
    async def delete(self,ctx,*,name:str=None):
        if name is not None:
            message = 
            await self.bot.say(
                'Are you sure you want to delete alert "{}" with message "{}"'
                .format(
    '''
def setup(bot):
    bot.add_cog(alarm(bot))
