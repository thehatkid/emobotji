import logging
import yaml
import re
from io import BytesIO
import aiohttp
from utils.database import Database
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class CogCommandsMisc(commands.Cog):
    """Misc commands category."""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.db: Database = bot.db
        self.http = aiohttp.ClientSession(
            loop=bot.loop, read_timeout=10,
            headers={'User-Agent': cfg['bot']['user-agent']}
        )

    def cog_unload(self):
        # Cog unloading callback
        async def close_http_session():
            await self.http.close()
        self.bot.loop.create_task(close_http_session())

    @commands.command(name='info', description='Shows an embed with emoji infomation by name. Who created, when emoji was uploaded, etc.')
    async def cmd_info(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if ctx.channel.is_nsfw() else False

        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)

        emoji = await self.db.get_emoji(name)
        if emoji is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot.', mention_author=False)
        else:
            embed = disnake.Embed(title=f':information_source: Emoji `{name}`', colour=disnake.Colour.blurple())
            if not is_nsfw and emoji['nsfw']:
                embed.description = '*Preview of Emoji are unavailable because that\'s NSFW*'
            else:
                embed.set_image(url='https://cdn.discordapp.com/emojis/{0}.{1}?size=512'.format(
                    emoji['id'],
                    'gif' if emoji['animated'] else 'png'
                ))
            embed.add_field(name='Uploaded by:', value='<@{0}>{1}'.format(
                emoji['author_id'], ' *(is you!)*' if emoji['author_id'] == ctx.author.id else ''
            ), inline=False)
            embed.add_field(name='Created at:', value='<t:{0}:f> (<t:{0}:R>)'.format(int(emoji['created_at'].timestamp())), inline=False)
            embed.add_field(name='Animated?', value='Yes' if emoji['animated'] else 'No', inline=False)
            embed.add_field(name='NSFW?', value='Yes' if emoji['nsfw'] else 'No', inline=False)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='big', description='Posts full-sized image of emoji.')
    async def cmd_big(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if ctx.channel.is_nsfw() else False
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        emoji = await self.db.get_emoji(name)
        if emoji is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot.', mention_author=False)
        else:
            if not is_nsfw and emoji['nsfw']:
                await ctx.reply(':x: Emoji are unavailable for posting here because that\'s **NSFW**.', mention_author=False)
            else:
                image_format = 'gif' if emoji['animated'] else 'png'
                url = 'https://cdn.discordapp.com/emojis/{0}.{1}?size=512'.format(emoji['id'], image_format)
                async with self.http.get(url) as response:
                    image = BytesIO(await response.read())
                await ctx.send(
                    content='<{0}:{1}:{2}>'.format('a' if emoji['animated'] else '', emoji['name'], emoji['id']),
                    file=disnake.File(fp=image, filename='{0}.{1}'.format(emoji['name'], image_format))
                )

    @commands.command(name='react', description='Reacts message with emoji.')
    async def cmd_react(self, ctx: commands.Context, name: str, message_id: int):
        try:
            msg = await ctx.fetch_message(message_id)
        except disnake.errors.NotFound:
            await ctx.reply(':x: Message not found or not from this channel.', mention_author=False)
        else:
            emoji = await self.db.get_emoji(name)
            if emoji is None:
                await ctx.reply(f':x: Emoji with name `{name}` not found in bot.', mention_author=False)
            else:
                if emoji['nsfw']:
                    await ctx.reply(':x: You can\'t react message because your selected emoji was marked as **NSFW only**.', mention_author=False)
                else:
                    await msg.add_reaction(self.bot.get_emoji(emoji['id']))


def setup(bot):
    bot.add_cog(CogCommandsMisc(bot))
    log.info('Loaded cog.')


def teardown(bot):
    log.info('Unloaded cog.')
