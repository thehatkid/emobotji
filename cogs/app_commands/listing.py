import logging
from math import ceil
from utils.database import Database
from utils.views import ViewPaginator
import disnake
from disnake import Option
from disnake import OptionType
from disnake.ext import commands

logger = logging.getLogger(__name__)


class AppCmdsListing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.slash_command(
        name='list',
        description='Shows an embed with emoji list',
        options=[
            Option('page', 'The number of emoji list page', OptionType.integer, False)
        ]
    )
    async def scmd_list(self, inter: disnake.AppCmdInter, page: int = 1):
        EMOJI_LIST = await self.db.get_emoji_list(inter.channel.nsfw)

        if len(EMOJI_LIST) == 0:
            return await inter.response.send_message(':x: Bot not have any emojis', ephemeral=True)

        embeds = []
        position = 0
        limit = 15
        total = ceil(len(EMOJI_LIST) / limit)

        if page > total:
            page = total

        while True:
            embed = disnake.Embed(title='Bot Emoji List', color=disnake.Colour.blurple(), description='')

            try:
                for i in range(0 + position, limit + position):
                    embed.description += '<{2}:{1}:{0}> [\\:{1}:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                        EMOJI_LIST[i][0],
                        EMOJI_LIST[i][1],
                        'a' if EMOJI_LIST[i][2] else '',
                        'gif' if EMOJI_LIST[i][2] else 'png',
                        ' *(NSFW)*' if EMOJI_LIST[i][3] else ''
                    )
            except IndexError:
                embeds.append(embed)
                break
            else:
                position += limit
                embeds.append(embed)

        view = ViewPaginator(inter.author, embeds, len(EMOJI_LIST), page - 1)
        view.msg = await inter.response.send_message(
            embed=embeds[page - 1],
            view=view
        )

    @commands.slash_command(
        name='search',
        description='Searches an emoji list with given query',
        options=[
            Option('query', 'The query of emoji to find', OptionType.string, True)
        ]
    )
    async def scmd_search(self, inter: disnake.AppCmdInter, query: str):
        EMOJI_LIST = await self.db.get_emoji_list_by_name(query, inter.channel.nsfw)

        if len(EMOJI_LIST) == 0:
            return await inter.response.send_message(f':x: Emoji with name/word `{query}` not exists or not found.', ephemeral=True)

        embeds = []
        position = 0
        limit = 15

        while True:
            embed = disnake.Embed(title=f'Found list by word: `{query}`', color=disnake.Colour.blurple(), description='')

            try:
                for i in range(0 + position, limit + position):
                    embed.description += '<{2}:{1}:{0}> [\\:{1}:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                        EMOJI_LIST[i][0],
                        EMOJI_LIST[i][1],
                        'a' if EMOJI_LIST[i][2] else '',
                        'gif' if EMOJI_LIST[i][2] else 'png',
                        ' *(NSFW)*' if EMOJI_LIST[i][3] else ''
                    )
            except IndexError:
                embeds.append(embed)
                break
            else:
                position += limit
                embeds.append(embed)

        view = ViewPaginator(inter.author, embeds, len(EMOJI_LIST))
        view.msg = await inter.response.send_message(
            embed=embeds[0],
            view=view
        )


def setup(bot: commands.Bot):
    cog = AppCmdsListing(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
