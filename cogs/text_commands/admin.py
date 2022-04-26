import logging
from disnake.ext import commands

log = logging.getLogger(__name__)


class TextCmdsAdmin(commands.Cog, name='Bot Developer only'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name='admin', description='Bot Developer only commands', hidden=True)
    @commands.is_owner()
    async def cmd_admin(self, ctx: commands.Context):
        pass

    @cmd_admin.command(name='load', description='Loads a bot extensions/cogs without restarting bot', hidden=True)
    async def cmd_admin_load(self, ctx: commands.Context, which: str):
        try:
            self.bot.load_extension(which)
        except commands.ExtensionNotFound:
            await ctx.reply(f':x: Extension `{which}` was not found')
        except commands.ExtensionAlreadyLoaded:
            await ctx.reply(f':x: Extension `{which}` is already loaded')
        except commands.ExtensionFailed as exc:
            await ctx.reply(f':x: Failed to reload extension: `{exc}`')
        else:
            await ctx.reply(f':white_check_mark: Loaded extension: {which}')

    @cmd_admin.command(name='unload', description='Unloads a bot extensions/cogs without restarting bot', hidden=True)
    async def cmd_admin_unload(self, ctx: commands.Context, which: str):
        try:
            self.bot.unload_extension(which)
        except commands.ExtensionNotFound:
            await ctx.reply(f':x: Extension `{which}` was not found')
        except commands.ExtensionNotLoaded:
            await ctx.reply(f':x: Extension `{which}` is already unloaded')
        except commands.ExtensionFailed as exc:
            await ctx.reply(f':x: Failed to reload extension: `{exc}`')
        else:
            await ctx.reply(f':white_check_mark: Unloaded extension: {which}')

    @cmd_admin.command(name='reload', description='Reloads a bot extensions/cogs for apply changes', hidden=True)
    async def cmd_admin_reload(self, ctx: commands.Context, which: str):
        try:
            self.bot.reload_extension(which)
        except commands.ExtensionNotFound:
            await ctx.reply(f':x: Extension `{which}` was not found')
        except commands.ExtensionNotLoaded:
            await ctx.reply(f':x: Extension `{which}` is unloaded')
        except commands.ExtensionFailed as exc:
            await ctx.reply(f':x: Failed to reload extension: `{exc}`')
        else:
            await ctx.reply(f':white_check_mark: Reloaded extension: {which}')


def setup(bot: commands.Bot):
    cog = TextCmdsAdmin(bot)
    bot.add_cog(cog)
    log.info('Loaded')


def teardown(bot):
    log.info('Unloaded')
