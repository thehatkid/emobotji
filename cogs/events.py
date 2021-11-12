import logging
import sys
import traceback
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)


class Events(commands.Cog):
    """Events cog for Discord Bot."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info('Bot is ready as {}'.format(self.bot.user))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        log.info('Bot has been invited to: [Name: {0}, ID: {1}]'.format(guild.name, guild.id))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        log.info('Bot has been kicked from: [Name: {0}, ID: {1}]'.format(guild.name, guild.id))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            # Missing command argument error
            await ctx.send(f':x: Required Argument: `{error.param}`')
        elif isinstance(error, commands.errors.CheckFailure):
            # Command access error
            await ctx.send(':x: You don\'t have access to this command.')
        elif isinstance(error, commands.errors.BadArgument):
            # Invalid command argument error
            await ctx.send(f':x: Bad Argument: `{error}`')
        elif isinstance(error, commands.CommandNotFound):
            # Command not found error
            pass
        elif isinstance(error, commands.errors.DisabledCommand):
            # Disabled command error
            await ctx.send(':x: This command was been disabled.')
        else:
            # Other error (traceback in console)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Events(bot))
    log.info('Loaded cog.')


def teardown(bot):
    log.info('Unloaded cog.')
