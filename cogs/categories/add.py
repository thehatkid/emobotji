import asyncio
from datetime import datetime
import logging
import yaml
import re
import aiohttp
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class CogCommandsAdd(commands.Cog):
    """Emojis addiction commands category."""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.db = bot.db
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

    @commands.command(name='add', description='Adds custom emoji to Bot.')
    async def cmd_add(self, ctx: commands.Context, name: str, emoji: str, nsfw: str = '0'):
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        if await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` = :name', {'name': name}):
            return await ctx.reply(f':x: `{name}` is already taken, try other name.', mention_author=False)

        NSFW = True if nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'yeah', 'y', 'true', '18+'] else False

        match = self.REGEX_EMOJI.match(emoji)
        if match is None:
            return await ctx.reply(f':x: `{emoji}`: That\'s not an emoji.', mention_author=False)
        animated, emoji_id = match.groups()

        async with self.http.get('https://cdn.discordapp.com/emojis/{0}.{1}?size=128'.format(emoji_id, 'gif' if animated else 'png')) as response:
            image = await response.read()

        if animated:
            guild = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_animated` < 50 ORDER BY `number` ASC LIMIT 1')
        else:
            guild = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_static` < 50 ORDER BY `number` ASC LIMIT 1')
        if guild is None:
            return await ctx.reply(':x: Emoji was not uploaded: `NO_FREE_AVAILABLE_GUILDS`', mention_author=False)
        guild = self.bot.get_guild(guild[0])

        try:
            result = await guild.create_custom_emoji(name=name, image=image, reason=f'Addition Requested by {ctx.author.id}')
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                await ctx.reply(f':x: Bot have rate limited.\n`{e}`', mention_author=False)
            else:
                await ctx.reply(f':x: Emoji was not added to bot.\n`{e}`', mention_author=False)
        else:
            await self.db.execute(
                'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `created`, `author_id`, `guild_id`) VALUES (:id, :name, :animated, :nsfw, :created, :author_id, :guild_id)',
                {'id': result.id, 'name': result.name, 'animated': result.animated, 'nsfw': NSFW, 'created': datetime.utcnow(), 'author_id': ctx.author.id, 'guild_id': guild.id}
            )
            if animated:
                await self.db.execute('UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            else:
                await self.db.execute('UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            if NSFW:
                await ctx.reply(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage.', mention_author=False)
            else:
                await ctx.reply(f':white_check_mark: Emoji {result} was added to bot.', mention_author=False)

    @commands.command(name='add-from-url', description='Adds emoji from URL with Image.')
    async def cmd_addfromurl(self, ctx: commands.Context, name: str, url: str, nsfw: str = '0'):
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        if await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` = :name', {'name': name}):
            return await ctx.reply(f':x: `{name}` is already taken, try other name.', mention_author=False)

        NSFW = True if nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'yeah', 'y', 'true', '18+'] else False

        try:
            async with self.http.get(url) as response:
                if response.status == 200:
                    if response.headers['content-type'] not in ['image/png', 'image/jpeg', 'image/gif']:
                        return await ctx.reply(':x: Requested URL is not an **image**.', mention_author=False)
                    animated = True if response.headers['content-type'] == 'image/gif' else False
                    image = await response.read()
                else:
                    return await ctx.reply(f':x: Got error while downloading image from URL. Status: `{response.status}`', mention_author=False)
        except asyncio.exceptions.TimeoutError:
            return await ctx.reply(':x: Timeout while downloading image from URL.', mention_author=False)
        except aiohttp.client_exceptions.InvalidURL:
            return await ctx.reply(':x: Invalid URL.', mention_author=False)
        except Exception as e:
            return await ctx.reply(f':x: Exception while downloading image from URL.\n`{e}`', mention_author=False)

        if animated:
            row = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_animated` < 50 ORDER BY `number` LIMIT 1')
        else:
            row = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_static` < 50 ORDER BY `number` LIMIT 1')
        if row is None:
            return await ctx.reply(':x: Emoji was not uploaded: `NO_AVAILABLE_GUILDS`', mention_author=False)
        guild = self.bot.get_guild(row[0])

        try:
            result = await guild.create_custom_emoji(name=name, image=image, reason=f'Addition Requested by {ctx.author.id}')
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                await ctx.reply(f':x: Bot have rate limited.\n`{e}`', mention_author=False)
            else:
                await ctx.reply(f':x: Emoji was not added to bot.\n`{e}`', mention_author=False)
        else:
            await self.db.execute(
                'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `created`, `author_id`, `guild_id`) VALUES (:id, :name, :animated, :nsfw, :created, :author_id, :guild_id)',
                {'id': result.id, 'name': result.name, 'animated': result.animated, 'nsfw': NSFW, 'created': datetime.utcnow(), 'author_id': ctx.author.id, 'guild_id': guild.id}
            )
            if animated:
                await self.db.execute('UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            else:
                await self.db.execute('UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            if NSFW:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage.', mention_author=False)
            else:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot.', mention_author=False)


def setup(bot):
    bot.add_cog(CogCommandsAdd(bot))
    log.info(f'Loaded cog: {__name__}')


def teardown(bot):
    log.info(f'Unloaded cog: {__name__}')
