import discord
from discord.ext import commands

class memes:
        def __init__(self,bot):
                self.bot=bot

        @commands.command()
        async def think(self):
                """Stop and think for a second. Maybe 30."""
                await self.bot.say(
                        ":thought_balloon:\n:thinking:")

        @commands.command()
        async def fku(self):
                """If you're feeling pretty angry"""
                await self.bot.say(":middle_finger:")

        @commands.command()
        async def lenny(self):
                """( ͡° ͜ʖ ͡°)"""
                await self.bot.say("( ͡° ͜ʖ ͡°)")
                
def setup(bot):
    bot.add_cog(memes(bot))
