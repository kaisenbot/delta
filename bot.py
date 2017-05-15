
import asyncio
from datetime import datetime
import json
import logging
import requests.packages.urllib3
import sys
import traceback

import discord
from discord.ext import commands

from cogs.util import checks

logging.basicConfig(level=logging.INFO)
requests.packages.urllib3.disable_warnings()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'))
default_ext = ['cogs.alerts', 'cogs.general', 'cogs.memes']

@bot.event
async def on_command_error(error, ctx):
        if isinstance(error, commands.NoPrivateMessage):
                await bot.send_message(ctx.message.author, ":x: not usable in pms")
        elif isinstance(error, commands.CommandInvokeError):
                print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
                traceback.print_tb(error.original.__traceback__)
                print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)


@bot.event
async def on_message(message):
        await bot.process_commands(message)


@bot.event
async def on_ready():
        print("\nLogged in as\n{0}:{1}\n"
              .format(bot.user.name, bot.user.id))
        if not hasattr(bot, 'uptime'):
                bot.uptime = datetime.utcnow()


@bot.event
async def on_server_join(server):
        await bot.send_message(server.default_channel, 'Did someone call?')
        user_arr = []
        for member in server.members:
                user_info = {
                        "Username": str(member),
                        "Snowflake ID": member.id,
                        "Balance": 0
                        }
                user_arr.append(user_info)
                with open('data.json', 'w') as db:
                    json.dump(user_arr, db, sort_keys=True)


@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def load(ctx, *, ext_name=None):
        """Loads an extension"""
        try:
                if ext_name is not None:
                        bot.load_extension(ext_name)
                        await bot.say(":ok_hand:")
        except(AttributeError, ImportError) as e:
                await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))


@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def reload(ctx, *, ext_name=None):
        try:
                if ext_name is not None:
                        bot.unload_extension(ext_name)
                        bot.load_extension(ext_name)
                        await bot.say(":ok_hand:")
        except(AttributeError, ImportError) as e:
                await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))


@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def unload(ctx, *, ext_name=None):
        """Unloads an extension"""
        if ext_name is not None:
                bot.unload_extension(ext_name)
                await bot.say(":ok_hand:")

if __name__ == "__main__":
        bot.remove_command('help')
        for ext in default_ext:
                try:
                        bot.load_extension(ext)
                except Exception as e:
                        print("{}: {}".format(e).__name__, e)
                        print("Loading of extension {} failed!".format(ext))
        bot.run('')
