import discord
from discord.ext import commands
from cogs.util import checks
from cogs.util import host

import asyncio
import collections
from datetime import datetime
import json
import psutil
import pytz

class general:
        def __init__(self,bot):
                self.bot = bot
                self.db = json.loads(open('data.json').read())
                self.tz = pytz.timezone('US/Eastern')
                self.help_menu = None
                    
        def get_uptime(self,brief=False):
                now = datetime.utcnow()
                delta = now - self.bot.uptime
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                days, hours = divmod(hours, 24)

                if not brief:
                    if days:
                        fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
                    else:
                        fmt = '{h} hours, {m} minutes, and {s} seconds'
                else:
                    fmt = '{h}h {m}m {s}s'
                    if days:
                        fmt = '{d}d ' + fmt

                return fmt.format(d=days, h=hours, m=minutes, s=seconds)

        def fetch_help(self):
                cog_info = {}
                commands = self.bot.commands
                cogs = self.bot.cogs
                
                for cog in sorted(cogs):
                        cog_commands = ""
                        for name in sorted(commands):
                                command = self.bot.get_command(name)
                                if command.hidden is False and command.cog_name==cog:
                                        cog_commands=("{}►`{}`: {}\n".format(
                                                cog_commands,name,command.short_doc))
                        cog_info[cog] = cog_commands
                        
                return collections.OrderedDict(sorted(cog_info.items()))
        
        def search(self, term):
                data = None
                
                if term is not None:
                        for dict in self.db:
                                for key,value in dict.items():
                                        if value == term:
                                                data = dict
                                                
                return data

        def time_now(self):
                
                return datetime.strftime(
                        datetime.now(self.tz),"%a, %b %d %I:%M %p %Z")
                    
        @commands.command(pass_context=True)
        async def help(self,ctx):
                """Brings up this menu"""
                if self.help_menu is None:
                        self.help_menu = self.fetch_help()
                        
                help_menu = self.help_menu

                if ctx.message.server is not None:
                        await self.bot.delete_message(ctx.message)
                sending_help = await self.bot.reply(
                        "unless you need an :ambulance: sending you help",
                        delete_after=15)

                em = discord.Embed(colour=discord.Colour.dark_purple())
                em.set_author(name="Help",icon_url=self.bot.user.avatar_url)
                em.set_thumbnail(url="http://i.imgur.com/ecSw4c4.png")
                for cog,commands in help_menu.items():
                        em.add_field(name=cog,value=commands)
                em.set_footer(text="Use prefix '/' or mention the bot to call these commands")        
                await self.bot.whisper(embed=em)
                
        @commands.command(pass_context=True)
        async def invite(self,ctx):
                """Invite me to other servers"""
                invite_url = discord.utils.oauth_url(
                        client_id=self.bot.user.id,
                        permissions=discord.Permissions.all())
                em = discord.Embed(title="Need an invite?",
                                   colour=discord.Color.dark_purple(),url=invite_url)
                em.set_footer(text="Invite me to your other discords!",
                              icon_url=self.bot.user.avatar_url)
                await self.bot.say(embed=em)

        @commands.command(pass_context=True,hidden=True)
        @checks.is_owner()
        async def log(self,ctx):
                user_arr = []
                await self.bot.delete_message(ctx.message)
                for member in ctx.message.server.members:
                        user_info = {
                                "Username":str(member),
                                "Snowflake ID":member.id,
                                "Balance":0
                                }
                        user_arr.append(user_info)
                        with open('data.json', 'w') as db:
                            json.dump(user_arr, db, sort_keys=True)
                self.db = json.loads(open('data.json').read())
                await self.bot.say(":white_check_mark:")
        
        @commands.command(aliases=['prune'],pass_context=True,no_pm=True)
        @checks.is_owner()
        async def purge(self,ctx,*,messages:int=None):
                """Purges specified amount of messages"""
                if messages is not None:
                        messages = messages+1
                        if messages <= 100 and messages > 0:
                                await self.bot.purge_from(
                                         ctx.message.channel,
                                         limit=messages)
                        elif messages > 100:
                                for x in range(messages//100):
                                        await self.bot.purge_from(
                                                ctx.message.channel,
                                                limit=100)
                                        await asyncio.sleep(3)
                                        await self.bot.purge_from(
                                                ctx.message.channel,
                                                limit=messages%100)

        @commands.command()
        async def stats(self):
                """Display host info"""
                em_loading = discord.Embed(
                        title=":arrows_counterclockwise: Loading...")
                loading = await self.bot.say(embed=em_loading)
                stats = host.host_info()
                statistics = collections.OrderedDict(
                        [("Uptime",'{}'.format(self.get_uptime(self))),
                         ("CPU Usage (%)",'{}'.format(stats[0])),
                         ("Logical Cores",'{}'.format(stats[1])),
                         ("Bot Usage",'{} Mb'.format(round(
                                 psutil.Process().memory_full_info().uss/1024**2))),
                         ("Available Mem",'{} Mb'
                         .format(stats[3])),
                         ("Physical Cores",'{}'.format(stats[2]))
                         ])
                
                em_stats = discord.Embed(colour=discord.Colour.dark_purple())
                em_stats.set_author(name="Statistics",
                                    icon_url=self.bot.user.avatar_url)
                for key,val in statistics.items():
                        em_stats.add_field(name=key,value='`{}`'.format(val))  
                await self.bot.edit_message(loading,embed=em_stats)
                        
        @commands.command(pass_context=True,no_pm=True)
        async def user(self,ctx,*,term=None):
                """User lookup service. Accepts user id, mentions, or name with discriminator."""
                user_info = None
                user_obj = None
                
                if term is None:
                        user_info = self.search(ctx.message.author.id)
                else:
                        if len(ctx.message.raw_mentions) > 0:
                                term = ctx.message.raw_mentions[0]
                        user_info = self.search(term)
                        
                if user_info is not None:
                        #Server lookup
                        user_info = collections.OrderedDict(user_info)
                        user_obj = discord.utils.get(ctx.message.server.members,
                                                     id=user_info['Snowflake ID'])
                        
                        em = discord.Embed(colour=discord.Color.dark_purple())
                        em.set_author(name=user_obj.name,
                                      icon_url=user_obj.avatar_url)
                        em.set_footer(text="Requested by {0} on {1}"
                                      .format(ctx.message.author,self.time_now())
                                      ,icon_url=self.bot.user.avatar_url)
                        for key,val in user_info.items():
                                em.add_field(name=key,value='`{}`'.format(val))
                                
                        await self.bot.say(embed=em)
                else:
                        await self.bot.say(":x: no such user found")
                
def setup(bot):
    bot.add_cog(general(bot))
    
