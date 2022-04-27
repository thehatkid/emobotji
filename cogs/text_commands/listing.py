import logging
from math import ceil
from utils.database import Database
from utils.views import ViewPaginator
import disnake
from disnake.ext import commands

log = logging.getLogger(__name__)


class TextCmdsListing(commands.Cog, name='Listing'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.command(name='list', description='Shows an embed with bot emoji list')
    async def cmd_list(self, ctx: commands.Context, page: int = 1):
        if isinstance(ctx.channel, disnake.TextChannel):
            nsfw = ctx.channel.nsfw
        else:
            nsfw = False

        if nsfw:
            EMOJI_LIST = await self.db.get_emoji_list(True)
        else:
            EMOJI_LIST = await self.db.get_emoji_list(False)

        if len(EMOJI_LIST) == 0:
            return await ctx.reply(':x: Bot not have any emojis')

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

        view = ViewPaginator(ctx.author, embeds, len(EMOJI_LIST), page - 1)
        view.msg = await ctx.reply(embed=embeds[page - 1], view=view)

    @commands.command(name='search', description='Searches an bot emoji list with given name/word', aliases=['find'])
    async def cmd_search(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.TextChannel):
            nsfw = ctx.channel.nsfw
        else:
            nsfw = False

        if nsfw:
            EMOJI_LIST = await self.db.get_emoji_list_by_name(name, True)
        else:
            EMOJI_LIST = await self.db.get_emoji_list_by_name(name, False)

        if len(EMOJI_LIST) == 0:
            return await ctx.reply(f':x: Emoji with name/word `{name}` not exists or not found')

        embeds = []
        position = 0
        limit = 15

        while True:
            embed = disnake.Embed(title=f'Found list by word: `{name}`', color=disnake.Colour.blurple(), description='')
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

        view = ViewPaginator(ctx.author, embeds, len(EMOJI_LIST))
        view.msg = await ctx.reply(embed=embeds[0], view=view)


def setup(bot: commands.Bot):
    cog = TextCmdsListing(bot)
    bot.add_cog(cog)
    log.info('Loaded')


def teardown(bot):
    log.info('Unloaded')
