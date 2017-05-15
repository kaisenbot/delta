import discord
from discord.ext import commands
import asyncio


class alerts:
    # TODO: Add support for multiple alert and timer tasks
    def __init__(self, bot):
        self.bot = bot

        self.alert_list = {}
        self._seconds = 0

    async def repeat(self, channel, message, interval):
        """Async task that repeatedly sends passed message to specified channel at rate of interval in minutes.
        Will spam server's default channel after 1 hour of no reset."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            last_check = self._seconds / 3600

            if last_check >= 1:
                await self.bot.send_message(
                    channel.server.default_channel,
                    "@everyone no one has checked walls in `{}` hours"
                        .format(last_check))
                await asyncio.sleep(1800)
            elif last_check >= 0.5:
                await self.bot.send_message(channel, message)
                await asyncio.sleep(interval)

    async def timer(self):
        """Increases attr `seconds` by 60 every minute"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            await asyncio.sleep(60)
            self._seconds += 60

    async def wait_for_input(self, ctx):
        """Returns message from bot.wait_for_message. Timeout is 60 seconds."""
        message = await self.bot.wait_for_message(
            timeout=60,
            author=ctx.message.author,
            channel=ctx.message.channel)
        return message

    @commands.group(pass_context=True)
    async def alert(self, ctx):
        """Access alert commands with /alert <subcommand> <arguments>;
        To see a list of alert commands, simply use /alert."""
        if ctx.invoked_subcommand is None:
            em = discord.Embed(colour=discord.Colour.dark_purple(),
                               description="Configure custom alerts for your server!")
            em.set_author(name="Alert", icon_url=self.bot.user.avatar_url)

            await self.bot.say(embed=em)

    @alert.command(pass_context=True)
    async def clear(self, ctx):
        """Reset alert timer to 0, otherwise it will remind guild's default channel after an hour every half hour.
        Usage: /alert clear"""
        self._seconds = 0
        await self.bot.say("Timer reset by {0.mention}. Thanks!"
                           .format(ctx.message.author), delete_after=5)

    @alert.command(pass_context=True)
    async def create(self, ctx, *, name: str):
        """Create a new alert to go off at a set interval.
        Usage: /alerts create <alert name>"""
        await self.bot.say(
            "Enter the message you would like to be reminded in {0.mention}"
                .format(ctx.message.channel))
        message = await self.wait_for_input(ctx)

        if message is not None:
            await self.bot.say(
                "How often would you like to be reminded of this? Minimum interval is 1 minute")
            interval = await self.wait_for_input(ctx)

            if interval is not None and interval.content.isdigit() is True:
                if int(interval.content) > 0:
                    await self.bot.say(
                        "Confirm alert with name \"{0}\", message \"{1}\", with interval of `{2}` minute(s) for "
                        "channel {3.mention}? Type `yes` to confirm. "
                            .format(name, message.content,
                                    interval.content, ctx.message.channel))
                    confirm = await self.bot.wait_for_message(
                        timeout=60,
                        author=ctx.message.author,
                        channel=ctx.message.channel,
                        content="yes")

                    if confirm is not None:
                        await self.bot.say(
                            ":white_check_mark: Alert confirmed!",
                            delete_after=15)
                        self.bot.loop.create_task(  # Creation of reminder
                            self.repeat(
                                ctx.message.channel,
                                message.content,
                                int(interval.content) * 60)
                        )
                        if not self.alert_list:
                            self.bot.loop.create_task(self.timer())
                        self.alert_list[name] = message.content
                        return  # Alert has been confirmed and created
        return await self.bot.say(":x: Alert creation failed!")  # If any timeouts occurred, shows generic failure message

    @alert.command()
    async def list(self):
        """Lists currently active alerts in a server."""
        line = ""
        if self.alert_list:
            for name, message in self.alert_list.items():
                line = "```{0}\n{1} | Last cleared: {2} minutes ago```"\
                    .format(line, name, self._seconds / 60)
                await self.bot.say(line)
                return
        await self.bot.say(
            "```No alerts found! Use /alert create <name> to start making a new one!```")


# Extension setup
def setup(bot):
    bot.add_cog(alerts(bot))
