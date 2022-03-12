import logging
from math import ceil
from utils.database import Database
from utils.views import ViewPaginator
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)


class CogCommandsListing(commands.Cog):
    """Emojis listing commands category."""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.db: Database = bot.db

    @commands.command(name='list', description='Shows an embed with emoji list')
    async def cmd_list(self, ctx: commands.Context, page: int = 1):
        if isinstance(ctx.channel, disnake.DMChannel):
            NSFW = False
        else:
            NSFW = True if ctx.channel.is_nsfw() else False

        if NSFW:
            EMOJI_LIST = await self.db.get_emoji_list(True)
        else:
            EMOJI_LIST = await self.db.get_emoji_list(False)

        if len(EMOJI_LIST) == 0:
            return await ctx.reply(':x: Bot not have any emojis.', mention_author=False)

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
                        EMOJI_LIST[i][0], # Emoji ID
                        EMOJI_LIST[i][1], # Emoji Name
                        'a' if EMOJI_LIST[i][2] else '', # Emoji is Animated?
                        'gif' if EMOJI_LIST[i][2] else 'png', # Emoji Format
                        ' *(NSFW)*' if EMOJI_LIST[i][3] else '' # NSFW marking
                    )
            except IndexError:
                embeds.append(embed)
                break
            else:
                position += limit
                embeds.append(embed)

        view = ViewPaginator(ctx.author, embeds, len(EMOJI_LIST), page - 1)
        view.msg = await ctx.send(embed=embeds[page - 1], view=view)

    @commands.command(name='search', description='Searching emoji in database.', aliases=['find'])
    async def cmd_search(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.DMChannel):
            NSFW = False
        else:
            NSFW = True if ctx.channel.is_nsfw() else False

        if NSFW:
            EMOJI_LIST = await self.db.get_emoji_list_by_name(name, True)
        else:
            EMOJI_LIST = await self.db.get_emoji_list_by_name(name, False)

        if len(EMOJI_LIST) == 0:
            return await ctx.reply(f':x: Emoji with name/word `{name}` not exists or not found.', mention_author=False)

        embeds = []
        position = 0
        limit = 15
        total = ceil(len(EMOJI_LIST) / limit)

        while True:
            embed = disnake.Embed(title=f'Found list by word: `{name}`', color=disnake.Colour.blurple(), description='')
            try:
                for i in range(0 + position, limit + position):
                    embed.description += '<{2}:{1}:{0}> [\\:{1}:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                        EMOJI_LIST[i][0], # Emoji ID
                        EMOJI_LIST[i][1], # Emoji Name
                        'a' if EMOJI_LIST[i][2] else '', # Emoji is Animated?
                        'gif' if EMOJI_LIST[i][2] else 'png', # Emoji Format
                        ' *(NSFW)*' if EMOJI_LIST[i][3] else '' # NSFW marking
                    )
            except IndexError:
                embeds.append(embed)
                break
            else:
                position += limit
                embeds.append(embed)

        view = ViewPaginator(ctx.author, embeds, len(EMOJI_LIST))
        view.msg = await ctx.send(embed=embeds[0], view=view)


def setup(bot):
    bot.add_cog(CogCommandsListing(bot))
    log.info('Loaded cog.')


def teardown(bot):
    log.info('Unloaded cog.')
