import logging
from math import ceil
import sys
import traceback
import asyncio
import discord
from discord.ext import commands
from discord_components import DiscordComponents


log = logging.getLogger(__name__)


async def bgTask_status(bot):
    while True:
        game = discord.Game('with emojis | prefix: e!')
        await bot.change_presence(activity=game, status=discord.Status.online)
        await asyncio.sleep(10)
        game = discord.Game('with emojis | help: e!help')
        await bot.change_presence(activity=game, status=discord.Status.online)
        await asyncio.sleep(10)


class Events(commands.Cog):
    """Events cog for Discord Bot."""
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_ready(self):
        await self.db.connect()
        self.bot.loop.create_task(bgTask_status(self.bot))
        DiscordComponents(self.bot)
        log.info('Bot is ready as {}'.format(self.bot.user))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log.info(
            'Bot has been invited to: [Name: {0}, ID: {1}]'.format(
                guild.name, guild.id
            )
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log.info(
            'Bot has been kicked from: [Name: {0}, ID: {1}]'.format(
                guild.name, guild.id
            )
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f':x: Required Argument: `{error.param}`')
        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send(':x: You don\'t have access to this command.')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f':x: Bad Argument: `{error}`')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Events(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
