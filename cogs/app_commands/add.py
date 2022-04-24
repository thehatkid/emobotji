import logging
import yaml
import re
import asyncio
import aiohttp
from datetime import datetime
from utils.database import Database
import disnake
from disnake import Option
from disnake import OptionType
from disnake.ext import commands

logger = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class AppCmdsAdd(commands.Cog):
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
            # Graceful close HTTP session
            await self.http.close()
        self.bot.loop.create_task(close_http_session())

    async def add_emoji_from_custom(self, inter: disnake.AppCmdInter, name: str, emoji: str, nsfw: bool):
        match = self.REGEX_EMOJI.match(emoji)
        if match is None:
            return await inter.response.send_message(f':x: `{emoji}`: That\'s not an emoji', ephemeral=True)
        animated, emoji_id = match.groups()

        await inter.response.defer()

        async with self.http.get(
            'https://cdn.discordapp.com/emojis/{0}.{1}?size=128'.format(
                emoji_id, 'gif' if animated else 'png'
            )
        ) as response:
            image = await response.read()

        if animated:
            guild_id = await self.db.get_available_guild('animated')
        else:
            guild_id = await self.db.get_available_guild('static')

        if guild_id is None:
            return await inter.edit_original_message(content=':x: Emoji was not uploaded: `NO_FREE_AVAILABLE_GUILDS`\nPlease, contact to Bot Developer')
        guild = self.bot.get_guild(guild_id)

        try:
            result = await guild.create_custom_emoji(name=name, image=image, reason=f'Addition Requested by {inter.author.id}')
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                await inter.edit_original_message(content=f':x: Bot has rate limited: `{e}`')
            else:
                await inter.edit_original_message(content=f':x: Emoji was not added to bot. Error: `{e}`')
        else:
            await self.db.add_emoji(result.id, result.name, result.animated, nsfw, datetime.utcnow(), inter.author.id, guild.id)

            if animated:
                await self.db.increase_usage_guild(guild.id, 'animated')
            else:
                await self.db.increase_usage_guild(guild.id, 'static')

            if nsfw:
                await inter.edit_original_message(content=f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage')
            else:
                await inter.edit_original_message(content=f':white_check_mark: Emoji {result} was added to bot')

    async def add_emoji_from_url(self, inter: disnake.AppCmdInter, name: str, url: str, nsfw: bool):
        await inter.response.defer()

        try:
            async with self.http.get(url) as response:
                if response.status == 200:
                    if response.headers['content-type'] not in ['image/png', 'image/jpeg', 'image/gif']:
                        return await inter.edit_original_message(content=':x: Requested URL is not an image')
                    animated = True if response.headers['content-type'] == 'image/gif' else False
                    image = await response.read()
                else:
                    return await inter.edit_original_message(content=f':x: Got error while downloading image from URL. HTTP Code: {response.status}')
        except asyncio.exceptions.TimeoutError:
            return await inter.edit_original_message(content=':x: Timeout while downloading image from URL')
        except aiohttp.InvalidURL:
            return await inter.edit_original_message(content=':x: Invalid URL')
        except Exception as e:
            return await inter.edit_original_message(content=f':x: Exception while downloading image from URL. Error: `{e}`')

        if animated:
            guild_id = await self.db.get_available_guild('animated')
        else:
            guild_id = await self.db.get_available_guild('static')

        if guild_id is None:
            return await inter.edit_original_message(content=':x: Emoji was not uploaded: `NO_FREE_AVAILABLE_GUILDS`\nPlease, contact to Bot Developer')
        guild = self.bot.get_guild(guild_id)

        try:
            result = await guild.create_custom_emoji(name=name, image=image, reason=f'Addition Requested by {inter.author.id}')
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                await inter.edit_original_message(content=f':x: Bot has rate limited: `{e}`')
            else:
                await inter.edit_original_message(content=f':x: Emoji was not added to bot. Error: `{e}`')
        else:
            await self.db.add_emoji(result.id, result.name, result.animated, nsfw, datetime.utcnow(), inter.author.id, guild.id)

            if animated:
                await self.db.increase_usage_guild(guild.id, 'animated')
            else:
                await self.db.increase_usage_guild(guild.id, 'static')

            if nsfw:
                await inter.edit_original_message(content=f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage')
            else:
                await inter.edit_original_message(content=f':white_check_mark: Emoji {result} was added to bot')

    @commands.slash_command(
        name='add',
        description='Adds custom emoji from server or URL with image to bot for further usage',
        options=[
            Option('name', 'The emoji name for further usage', OptionType.string, True),
            Option('emoji', 'The custom emoji from server for upload emoji to bot', OptionType.string, False),
            Option('url', 'The URL with image for upload emoji to bot', OptionType.string, False),
            Option('nsfw', 'Whether the emoji is NSFW or not', OptionType.boolean, False)
        ]
    )
    async def scmd_add(
        self,
        inter: disnake.AppCmdInter,
        name: str,
        emoji: str = None,
        url: str = None,
        nsfw: bool = False
    ):
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await inter.response.send_message(
                f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores',
                ephemeral=True
            )

        if await self.db.get_emoji(name) is not None:
            return await inter.response.send_message(
                f':x: `{name}` is already taken, try other emoji name',
                ephemeral=True
            )

        if emoji:
            await self.add_emoji_from_custom(inter, name, emoji, nsfw)
        elif url:
            await self.add_emoji_from_url(inter, name, url, nsfw)
        else:
            await inter.response.send_message(
                ':x: Please, specify the `emoji` or `url` command argument',
                ephemeral=True
            )


def setup(bot: commands.Bot):
    cog = AppCmdsAdd(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
