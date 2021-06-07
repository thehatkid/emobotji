import logging
from math import ceil
import sys
import traceback
import asyncio
import discord
from discord.ext import commands
from discord_components import DiscordComponents
from discord_components import InteractionType
from discord_components import Button
from discord_components import ButtonStyle


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

    @commands.Cog.listener()
    async def on_button_click(self, res):
        if res.component.id.startswith('list_'):
            if res.component.id == 'list_close':
                await res.respond(
                    type=InteractionType.UpdateMessage,
                    embed=discord.Embed(title=':x: List was closed.'),
                    components=[]
                )
            elif res.component.id.startswith('list_page:'):
                page = int(res.component.id.split(':')[1])
                count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis`')
                limit = 10
                total = ceil(count[0] / limit)
                if page > total:
                    page = total
                offset = (limit * page) - limit
                rows = await self.db.fetch_all(
                    'SELECT `id`, `name`, `animated` FROM `emojis` ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                    {'limit': limit, 'offset': offset}
                )
                embed = discord.Embed(title='Bot\'s Emoji List', colour=discord.Colour.blurple())
                embed.set_footer(text='Page: {0} of {1}'.format(page, total))
                desc = ''
                for emoji in rows:
                    if emoji[2]:
                        desc += '<a:{0}:{1}> :{0}:\n'.format(emoji[1], emoji[0])
                    else:
                        desc += '<:{0}:{1}> :{0}:\n'.format(emoji[1], emoji[0])
                if not desc:
                    desc = 'Empty...'
                embed.description = desc
                buttons = [
                    Button(
                        id='list_page:{}'.format(page - 1),
                        emoji=u'\U000025C0',
                        style=ButtonStyle.grey,
                        disabled=(True if page <= 1 else False)
                    ),
                    Button(
                        id='list_page:{}'.format(page + 1),
                        emoji=u'\U000025B6',
                        style=ButtonStyle.grey,
                        disabled=(True if page >= total else False)
                    ),
                    Button(
                        id='list_close',
                        emoji=u'\U00002716',
                        style=ButtonStyle.red
                    )
                ]
                await res.respond(
                    type=InteractionType.UpdateMessage,
                    embed=embed, components=[buttons]
                )


def setup(bot):
    bot.add_cog(Events(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
