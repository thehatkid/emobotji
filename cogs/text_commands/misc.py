import logging
import yaml
import re
from datetime import datetime
import calendar
from utils.database import Database
import disnake
from disnake.ext import commands

log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class TextCmdsMisc(commands.Cog, name='Miscellaneous'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.command(name='info', description='Shows an embed with emoji infomation by name')
    async def cmd_info(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.TextChannel):
            is_nsfw = ctx.channel.nsfw
        else:
            is_nsfw = False

        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores')

        emoji = await self.db.get_emoji(name)

        if emoji is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot')
        else:
            created_at = datetime.fromtimestamp(calendar.timegm(emoji['created_at'].timetuple()))
            created_field = '<t:{0}:f> (<t:{0}:R>)'.format(int(created_at.timestamp()))
            uploader_field = '<@{0}>'.format(emoji['author_id'])

            if emoji['author_id'] == ctx.author.id:
                uploader_field += ' *(is you!)*'

            embed = disnake.Embed(title=f':information_source: Emoji `{emoji["name"]}`', colour=disnake.Colour.blurple())

            if not is_nsfw and emoji['nsfw']:
                embed.description = '*Preview of Emoji are unavailable because that\'s NSFW*'
            else:
                embed.set_image(url='https://cdn.discordapp.com/emojis/{0}.{1}?size=512'.format(
                    emoji['id'],
                    'gif' if emoji['animated'] else 'png'
                ))

            embed.add_field(name='Uploaded by:', value=uploader_field, inline=False)
            embed.add_field(name='Created at:', value=created_field, inline=False)
            embed.add_field(name='Animated?', value='Yes' if emoji['animated'] else 'No', inline=False)
            embed.add_field(name='NSFW?', value='Yes' if emoji['nsfw'] else 'No', inline=False)

            await ctx.reply(embed=embed)

    @commands.command(name='react', description='Reacts message with emoji by message ID (also must be in same channel)')
    async def cmd_react(self, ctx: commands.Context, name: str, message_id: int):
        try:
            msg = await ctx.fetch_message(message_id)
        except disnake.errors.NotFound:
            await ctx.reply(':x: Message not found or not from this channel')
        else:
            emoji = await self.db.get_emoji(name)
            if emoji is None:
                await ctx.reply(f':x: Emoji with name `{name}` not found in bot')
            else:
                if emoji['nsfw']:
                    await ctx.reply(':x: You can\'t react message because your selected emoji was marked as **NSFW only**')
                else:
                    await msg.add_reaction(self.bot.get_emoji(emoji['id']))


def setup(bot: commands.Bot):
    cog = TextCmdsMisc(bot)
    bot.add_cog(cog)
    log.info('Loaded')


def teardown(bot):
    log.info('Unloaded')
