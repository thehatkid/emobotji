import logging
from utils.database import Database
import disnake
from disnake import Option
from disnake import OptionType
from disnake.ext import commands

logger = logging.getLogger(__name__)


class AppCmdsBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.slash_command(
        name='bot',
        description='Bot\'s commands'
    )
    async def scmd_bot(self, inter: disnake.AppCmdInter):
        pass


def setup(bot: commands.Bot):
    cog = AppCmdsBot(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
