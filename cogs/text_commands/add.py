import logging
import yaml
import re
import asyncio
import aiohttp
from datetime import datetime
from utils import fetch_image
from utils.database import Database
import disnake
from disnake.ext import commands

log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class TextCmdsAdd(commands.Cog, name='Add Emojis'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db
        self.http = aiohttp.ClientSession(
            loop=bot.loop, read_timeout=10,
            headers={'User-Agent': cfg['bot']['user-agent']}
        )
        self.REGEX_EMOJI = re.compile(
            r'\\?<(a?)\\?:[\w_]{2,32}\\?:(\d{12,24})\\?>',
            re.ASCII
        )

    def cog_unload(self):
        # Cog unloading callback
        async def close_http_session():
            await self.http.close()
        self.bot.loop.create_task(close_http_session())

    async def add_emoji_to_bot(self, ctx: commands.Context, name: str, image: bytes, animated: bool, nsfw: bool = False):
        if animated:
            guild_id = await self.db.get_available_guild('animated')
        else:
            guild_id = await self.db.get_available_guild('static')

        if guild_id is None:
            return await ctx.reply(':x: Emoji was not uploaded: `NO_FREE_AVAILABLE_GUILDS`\nPlease, contact to Bot Developer')
        guild = self.bot.get_guild(guild_id)

        try:
            result = await guild.create_custom_emoji(name=name, image=image, reason=f'Addition Requested by {ctx.author.id}')
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                await ctx.reply(f':x: Bot has rate limited: `{e}`')
            else:
                await ctx.reply(f':x: Emoji was not added to bot. Error: `{e}`')
        else:
            await self.db.add_emoji(result.id, result.name, result.animated, nsfw, datetime.utcnow(), ctx.author.id, guild.id)

            if animated:
                await self.db.increase_usage_guild(guild.id, 'animated')
            else:
                await self.db.increase_usage_guild(guild.id, 'static')

            if nsfw:
                await ctx.reply(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage')
            else:
                await ctx.reply(f':white_check_mark: Emoji {result} was added to bot')

    async def add_emoji_from_custom(self, ctx: commands.Context, name: str, emoji: str, nsfw: bool):
        match = self.REGEX_EMOJI.match(emoji)
        if match is None:
            return await ctx.reply(f':x: `{emoji}`: That\'s not an emoji')
        animated, emoji_id = match.groups()

        uri = 'https://cdn.discordapp.com/emojis/{0}.{1}?size=128'.format(
            emoji_id, 'gif' if animated else 'png'
        )
        data = await fetch_image(self.http, uri)

        if data[0] is False:
            return await ctx.reply(':x: Something went wrong while loading image')

        await self.add_emoji_to_bot(ctx, name, data[2], data[1], nsfw)

    async def add_emoji_from_url(self, ctx: commands.Context, name: str, url: str, nsfw: bool):
        try:
            data = await fetch_image(self.http, url)
        except aiohttp.InvalidURL:
            return await ctx.reply(':x: Invalid URL')
        except asyncio.exceptions.TimeoutError:
            return await ctx.reply(':x: Timeout while downloading image from URL')
        except Exception as exc:
            return await ctx.reply(f':x: Exception while downloading image from URL. Error: `{exc.__class__.__name__}: {exc}`')

        if data[0] is False:
            if data[1] == 1:
                await ctx.reply(':x: Requested URL is not an image')
            elif data[1] == 2:
                await ctx.reply(f':x: Got error while downloading image from URL. HTTP Code: {data[2]}')
            else:
                await ctx.reply(f':x: Something went wrong while loading image')
            return

        await self.add_emoji_to_bot(ctx, name, data[2], data[1], nsfw)

    @commands.command(name='add', description='Adds custom emoji from server to bot for further usage')
    async def cmd_add(self, ctx: commands.Context, name: str, emoji: str, nsfw: str = '0'):
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores')
        if await self.db.get_emoji(name):
            return await ctx.reply(f':x: `{name}` is already taken, try other emoji name')

        NSFW = True if nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'yeah', 'y', 'true', '18+'] else False

        await self.add_emoji_from_custom(ctx, name, emoji, NSFW)

    @commands.command(name='add-from-url', description='Adds emoji from URL with image to bot for further usage')
    async def cmd_addfromurl(self, ctx: commands.Context, name: str, url: str, nsfw: str = '0'):
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores')
        if await self.db.get_emoji(name):
            return await ctx.reply(f':x: `{name}` is already taken, try other emoji name')

        NSFW = True if nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'yeah', 'y', 'true', '18+'] else False

        await self.add_emoji_from_url(ctx, name, url, NSFW)


def setup(bot: commands.Bot):
    cog = TextCmdsAdd(bot)
    bot.add_cog(cog)
    log.info('Loaded')


def teardown(bot):
    log.info('Unloaded')
