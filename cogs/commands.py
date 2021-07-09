import asyncio
from io import BytesIO
import logging
import time
import re
import aiohttp
from os import environ
from math import ceil
import discord
from discord.ext import commands
from discord_components import Button
from discord_components import ButtonStyle
from discord_components import InteractionType


log = logging.getLogger(__name__)


class Commands(commands.Cog):
    """Commands cog for Discord Bot."""
    regex = re.compile(r'\\?<(a?)\\?:[\w_]{2,32}\\?:(\d{12,24})\\?>', re.ASCII)

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.http = aiohttp.ClientSession(
            loop=bot.loop, read_timeout=10,
            headers={'User-Agent': environ.get('USER_AGENT')}
        )

    def cog_unload(self):
        async def close_http_session():
            await self.http.close()
        self.bot.loop.create_task(close_http_session())

    @commands.command(name='reload', description='Reloads extenstion/cog (requires OWNER_ID)')
    @commands.check(lambda ctx: ctx.author.id == int(environ.get('OWNER_ID')))
    async def cmd_reload(self, ctx, which: str = 'all'):
        if which == 'all':
            self.bot.reload_extension('cogs.events')
            self.bot.reload_extension('cogs.commands')
            self.bot.reload_extension('cogs.help')
            self.bot.reload_extension('cogs.emoji')
        elif which == 'events':
            self.bot.reload_extension('cogs.events')
        elif which == 'commands':
            self.bot.reload_extension('cogs.commands')
        elif which == 'help':
            self.bot.reload_extension('cogs.help')
        elif which == 'emoji':
            self.bot.reload_extension('cogs.emoji')
        else:
            return await ctx.send('Which reload?\n`events`, `commands`, `help`, `emoji` or `all`.')
        return await ctx.send(':arrows_counterclockwise: Reloaded: `{}`'.format(which))

    @commands.command(name='ping', description='Pings bot.')
    async def cmd_ping(self, ctx):
        uptime = time.time() - self.bot.start_time
        time_d = int(uptime) / (3600 * 24)
        time_h = int(uptime) / 3600 - int(time_d) * 24
        time_min = int(uptime) / 60 - int(time_h) * 60 - int(time_d) * 24 * 60
        time_sec = int(uptime) - int(time_min) * 60 - int(time_h) * 3600 - int(time_d) * 24 * 60 * 60
        uptime_str = '%01d days, %02d hours, %02d minutes, %02d seconds' % (time_d, time_h, time_min, time_sec)
        embed = discord.Embed(
            title=':ping_pong: Pong!',
            colour=discord.Colour.blurple()
        )
        embed.set_footer(
            text='Requested by {0}#{1}'.format(
                ctx.author.name, ctx.author.discriminator
            ),
            icon_url=ctx.author.avatar_url
        )
        embed.add_field(
            name=':signal_strength: Bot\'s Latency',
            value='{}ms'.format(round(self.bot.latency * 1000)),
            inline=False
        )
        embed.add_field(
            name=':hourglass: Bot\'s Uptime',
            value=uptime_str,
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='list', description='Sends embed with emoji list.')
    async def cmd_list(self, ctx, page: int = 1):
        if isinstance(ctx.channel, discord.DMChannel):
            nsfw = False
        else:
            nsfw = True if ctx.channel.is_nsfw() else False
        if nsfw:
            count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis`')
        else:
            count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis` WHERE `nsfw` = 0')

        limit = 10
        total = ceil(count[0] / limit)

        if page > total:
            page = total

        offset = (limit * page) - limit

        if nsfw:
            rows = await self.db.fetch_all(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                {'limit': limit, 'offset': offset}
            )
        else:
            rows = await self.db.fetch_all(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `nsfw` = 0 ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                {'limit': limit, 'offset': offset}
            )

        embed = discord.Embed(title='Bot\'s Emoji List', colour=discord.Colour.blurple())
        embed.set_footer(text='Page: {0} of {1}'.format(page, total))
        desc = ''

        for emoji in rows:
            desc += '<{2}:{1}:{0}> [\:{1}\:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                emoji[0],
                emoji[1],
                'a' if emoji[2] else '',
                'gif' if emoji[2] else 'png',
                ' *(NSFW)*' if emoji[3] else ''
            )

        if not desc:
            desc = 'Empty...'
        embed.description = desc

        buttons = [
            Button(id='list_page:{}'.format(page - 1), emoji=u'\U000025C0', style=ButtonStyle.grey,disabled=True if page <= 1 else False),
            Button(id='list_page:{}'.format(page + 1), emoji=u'\U000025B6', style=ButtonStyle.grey, disabled=True if page >= total else False),
            Button(id='list_close', emoji=u'\U00002716', style=ButtonStyle.red)
        ]
        msg = await ctx.send(embed=embed, components=[buttons])

        def check(res):
            return res.message.id == msg.id and res.user.id == ctx.author.id and res.channel.id == ctx.channel.id

        while True:
            try:
                res = await self.bot.wait_for('button_click', check=check, timeout=120)
            except asyncio.TimeoutError:
                embed = discord.Embed(title=':x: List was closed.', description='Reason: *Timeout.*')
                await msg.edit(embed=embed, components=[])
                break
            else:
                if res.component.id == 'list_close':
                    embed = discord.Embed(title=':x: List was closed.', description='Reason: *Closed by user.*')
                    await res.respond(type=InteractionType.UpdateMessage, embed=embed, components=[])
                    break
                elif res.component.id.startswith('list_page:'):
                    page = int(res.component.id.split(':')[1])

                    if nsfw:
                        count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis`')
                    else:
                        count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis` WHERE `nsfw` = 0')

                    limit = 10
                    total = ceil(count[0] / limit)

                    if page > total:
                        page = total

                    offset = (limit * page) - limit

                    if nsfw:
                        rows = await self.db.fetch_all(
                            'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                            {'limit': limit, 'offset': offset}
                        )
                    else:
                        rows = await self.db.fetch_all(
                            'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `nsfw` = 0 ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                            {'limit': limit, 'offset': offset}
                        )

                    embed = discord.Embed(title='Bot\'s Emoji List', colour=discord.Colour.blurple())
                    embed.set_footer(text='Page: {0} of {1}'.format(page, total))
                    desc = ''

                    for emoji in rows:
                        desc += '<{2}:{1}:{0}> [\:{1}\:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                            emoji[0],
                            emoji[1],
                            'a' if emoji[2] else '',
                            'gif' if emoji[2] else 'png',
                            ' *(NSFW)*' if emoji[3] else ''
                        )

                    if not desc:
                        desc = 'Empty...'
                    embed.description = desc

                    buttons = [
                        Button(id='list_page:{}'.format(page - 1), emoji=u'\U000025C0', style=ButtonStyle.grey,disabled=True if page <= 1 else False),
                        Button(id='list_page:{}'.format(page + 1), emoji=u'\U000025B6', style=ButtonStyle.grey, disabled=True if page >= total else False),
                        Button(id='list_close', emoji=u'\U00002716', style=ButtonStyle.red)
                    ]
                    await res.respond(type=InteractionType.UpdateMessage, embed=embed, components=[buttons])

    @commands.command(name='search', description='Searching emoji in database.', aliases=['find'])
    async def cmd_search(self, ctx, name: str):
        if isinstance(ctx.channel, discord.DMChannel):
            nsfw = False
        else:
            nsfw = True if ctx.channel.is_nsfw() else False
        if nsfw:
            count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis` WHERE `name` LIKE :name', {'name': f'%{name}%'})
        else:
            count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis` WHERE `name` LIKE :name AND `nsfw` = 0', {'name': f'%{name}%'})

        page = 1
        limit = 10
        total = ceil(count[0] / limit)
        offset = (limit * page) - limit

        if nsfw:
            rows = await self.db.fetch_all(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                {'name': f'%{name}%', 'limit': limit, 'offset': offset}
            )
        else:
            rows = await self.db.fetch_all(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name AND `nsfw` = 0 ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                {'name': f'%{name}%', 'limit': limit, 'offset': offset}
            )

        embed = discord.Embed(title=f'Searching: `{name}`', colour=discord.Colour.blurple())
        embed.set_footer(text='Page: {0} of {1}'.format(page, total))
        desc = ''

        for emoji in rows:
            desc += '<{2}:{1}:{0}> [\:{1}\:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                emoji[0],
                emoji[1],
                'a' if emoji[2] else '',
                'gif' if emoji[2] else 'png',
                ' *(NSFW)*' if emoji[3] else ''
            )

        if not desc:
            desc = 'Empty...'
        embed.description = desc

        buttons = [
            Button(id='list_page:{}'.format(page - 1), emoji=u'\U000025C0', style=ButtonStyle.grey,disabled=True if page <= 1 else False),
            Button(id='list_page:{}'.format(page + 1), emoji=u'\U000025B6', style=ButtonStyle.grey, disabled=True if page >= total else False),
            Button(id='list_close', emoji=u'\U00002716', style=ButtonStyle.red)
        ]
        msg = await ctx.send(embed=embed, components=[buttons])

        def check(res):
            return res.message.id == msg.id and res.user.id == ctx.author.id and res.channel.id == ctx.channel.id

        while True:
            try:
                res = await self.bot.wait_for('button_click', check=check, timeout=120)
            except asyncio.TimeoutError:
                embed = discord.Embed(title=':x: List was closed.', description='Reason: *Timeout.*')
                await msg.edit(embed=embed, components=[])
                break
            else:
                if res.component.id == 'list_close':
                    embed = discord.Embed(title=':x: List was closed.', description='Reason: *Closed by user.*')
                    await res.respond(type=InteractionType.UpdateMessage, embed=embed, components=[])
                    break
                elif res.component.id.startswith('list_page:'):
                    page = int(res.component.id.split(':')[1])

                    if nsfw:
                        count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis` WHERE `name` LIKE :name', {'name': f'%{name}%'})
                    else:
                        count = await self.db.fetch_one('SELECT COUNT(*) FROM `emojis` WHERE `name` LIKE :name AND `nsfw` = 0', {'name': f'%{name}%'})

                    limit = 10
                    total = ceil(count[0] / limit)

                    if page > total:
                        page = total

                    offset = (limit * page) - limit

                    if nsfw:
                        rows = await self.db.fetch_all(
                            'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                            {'name': f'%{name}%', 'limit': limit, 'offset': offset}
                        )
                    else:
                        rows = await self.db.fetch_all(
                            'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name AND `nsfw` = 0 ORDER BY `name` ASC LIMIT :limit OFFSET :offset',
                            {'name': f'%{name}%', 'limit': limit, 'offset': offset}
                        )

                    embed = discord.Embed(title=f'Searching: `{name}`', colour=discord.Colour.blurple())
                    embed.set_footer(text='Page: {0} of {1}'.format(page, total))
                    desc = ''

                    for emoji in rows:
                        desc += '<{2}:{1}:{0}> [\:{1}\:](https://cdn.discordapp.com/emojis/{0}.{3}){4}\n'.format(
                            emoji[0],
                            emoji[1],
                            'a' if emoji[2] else '',
                            'gif' if emoji[2] else 'png',
                            ' *(NSFW)*' if emoji[3] else ''
                        )

                    if not desc:
                        desc = 'Empty...'
                    embed.description = desc

                    buttons = [
                        Button(id='list_page:{}'.format(page - 1), emoji=u'\U000025C0', style=ButtonStyle.grey,disabled=True if page <= 1 else False),
                        Button(id='list_page:{}'.format(page + 1), emoji=u'\U000025B6', style=ButtonStyle.grey, disabled=True if page >= total else False),
                        Button(id='list_close', emoji=u'\U00002716', style=ButtonStyle.red)
                    ]
                    await res.respond(type=InteractionType.UpdateMessage, embed=embed, components=[buttons])

    @commands.command(name='info', description='Gets emoji info by name. Who created, when emoji was uploaded, etc.')
    async def cmd_info(self, ctx, name: str):
        if isinstance(ctx.channel, discord.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if ctx.channel.is_nsfw() else False
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.send(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.')
        row = await self.db.fetch_one('SELECT `id`, `name`, `animated`, `nsfw`, `author_id`, `created` FROM `emojis` WHERE `name` LIKE :name', {'name': name})
        if row is None:
            await ctx.send(f':x: Emoji `{name}` not exists in bot.')
        else:
            embed = discord.Embed(title=f':information_source: Emoji `{name}`', colour=discord.Colour.blurple())

            if not is_nsfw and row[3]:
                embed.description = '*Preview of Emoji are unavailable because that\'s NSFW.*'
            else:
                embed.set_image(url='https://cdn.discordapp.com/emojis/{0}.{1}'.format(row[0], 'gif' if row[2] else 'png'))

            embed.add_field(name='Uploaded by:', value='{0}{1}'.format(row[4], ' *(is you!)*' if int(row[4]) == ctx.author.id else ''), inline=False)
            embed.add_field(name='Created at:', value='<t:{0}:f> ({1})'.format(int(row[5].timestamp()), 'UTC'), inline=False)
            embed.add_field(name='Animated?', value='Yes' if row[2] else 'No', inline=False)
            embed.add_field(name='NSFW?', value='Yes' if row[3] else 'No', inline=False)
            await ctx.send(embed=embed)

    @commands.command(name='big', description='Posts image of emoji.')
    async def cmd_big(self, ctx, name: str):
        if isinstance(ctx.channel, discord.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if ctx.channel.is_nsfw() else False
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.send(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.')
        row = await self.db.fetch_one('SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name', {'name': name})
        if row is None:
            await ctx.send(f':x: Emoji `{name}` not exists in bot.')
        else:
            if not is_nsfw and row[3]:
                await ctx.send(':x: Emoji are unavailable for posting here because that\'s **NSFW**.')
            else:
                image_format = 'gif' if row[2] else 'png'
                url = 'https://cdn.discordapp.com/emojis/{0}.{1}'.format(row[0], image_format)
                async with self.http.get(url) as response:
                    image = BytesIO(await response.read())
                await ctx.send(
                    content='<{0}:{1}:{2}>'.format('a' if row[2] else '', row[1], row[0]),
                    file=discord.File(fp=image, filename='{0}.{1}'.format(row[1], image_format))
                )

    @commands.command(name='add', description='Adds custom emoji.')
    async def cmd_add(self, ctx, name: str, emoji: str, is_nsfw: str = '0'):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.send(':x: Sorry, Webhooks and Bots can\'t add emojis to bot. 0_0')
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.send(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.')
        if await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` LIKE :name', {'name': name}):
            return await ctx.send(f':x: `{name}` is already taken, try other name.')
        if is_nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'y', 'true', '18+']:
            is_nsfw = True
        else:
            is_nsfw = False

        match = self.regex.match(emoji)
        if match is None:
            return await ctx.send(':x: That\'s not an emoji.')
        animated, emoji_id = match.groups()
        author = ctx.author.id

        url = 'https://cdn.discordapp.com/emojis/{0}.{1}'.format(emoji_id, 'gif' if animated else 'png')
        async with self.http.get(url) as response:
            image = await response.read()

        if animated:
            guild = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_animated` < 50 ORDER BY `number` ASC LIMIT 1')
        else:
            guild = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_static` < 50 ORDER BY `number` ASC LIMIT 1')
        if guild is None:
            return await ctx.send(':x: Emoji was not uploaded: `NO_AVAILABLE_GUILDS`')
        guild = self.bot.get_guild(guild[0])

        try:
            result = await guild.create_custom_emoji(
                name=name, image=image,
                reason=f'Addition Requested by {author}'
            )
        except discord.errors.HTTPException as e:
            if e.status == 429:
                await ctx.send(f':x: Bot have rate limited.\n`{e}`')
            await ctx.send(f':x: Emoji was not added to bot.\n`{e}`')
        else:
            await self.db.execute(
                'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `author_id`, `guild_id`) VALUES (:id, :name, :animated, :nsfw, :author_id, :guild_id)',
                {'id': result.id, 'name': result.name, 'animated': result.animated, 'nsfw': is_nsfw, 'author_id': author, 'guild_id': guild.id}
            )
            if animated:
                await self.db.execute('UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            else:
                await self.db.execute('UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            if is_nsfw:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage.')
            else:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot.')

    @commands.command(name='add-from-url', description='Adds emoji from URL with Image.')
    async def cmd_addfromurl(self, ctx, name: str, url: str, is_nsfw: str = '0'):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.send(':x: Sorry, Webhooks and Bots can\'t add emojis to bot. 0_0')
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.send(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.')
        if await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` LIKE :name', {'name': name}):
            return await ctx.send(f':x: `{name}` is already taken, try other name.')
        if is_nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'y', 'true', '18+']:
            is_nsfw = True
        else:
            is_nsfw = False

        author = ctx.author.id

        try:
            async with self.http.get(url) as response:
                if response.status == 200:
                    if response.headers['content-type'] not in {'image/png', 'image/jpeg', 'image/gif'}:
                        return await ctx.send(':x: Requested URL is not an **image**.')
                    animated = True if response.headers['content-type'] == 'image/gif' else False
                    image = await response.read()
                else:
                    return await ctx.send(f':x: Got error while downloading image from URL. Status: `{response.status}`')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(':x: Timeout while downloading image from URL.')
        except aiohttp.client_exceptions.InvalidURL:
            return await ctx.send(':x: Invalid URL.')
        except Exception as e:
            return await ctx.send(f':x: Exception while downloading image from URL.\n`{e}`')

        if animated:
            guild = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_animated` < 50 ORDER BY `number` LIMIT 1')
        else:
            guild = await self.db.fetch_one('SELECT `guild_id` FROM `guilds` WHERE `usage_static` < 50 ORDER BY `number` LIMIT 1')
        if guild is None:
            return await ctx.send(':x: Emoji was not uploaded: `NO_AVAILABLE_GUILDS`')
        guild = self.bot.get_guild(guild[0])

        try:
            result = await guild.create_custom_emoji(
                name=name, image=image,
                reason=f'Addition Requested by {author}'
            )
        except discord.errors.HTTPException as e:
            if e.status == 429:
                return await ctx.send(f':x: Bot have rate limited.\n`{e}`')
            await ctx.send(f':x: Emoji was not added to bot.\n`{e}`')
        else:
            await self.db.execute(
                'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `author_id`, `guild_id`) VALUES (:id, :name, :animated, :nsfw, :author_id, :guild_id)',
                {'id': result.id, 'name': result.name, 'animated': result.animated, 'nsfw': is_nsfw, 'author_id': author, 'guild_id': guild.id}
            )
            if animated:
                await self.db.execute('UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            else:
                await self.db.execute('UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            if is_nsfw:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage.')
            else:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot.')

    @commands.command(name='mark-nsfw', description='Marks emoji as NSFW usage only, also unmarks if was marked.', aliases=['nsfw', 'is-nsfw', 'toggle-nsfw'])
    async def cmd_marknsfw(self, ctx, name: str):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.send(':x: Sorry, Webhooks and Bots can\'t mark emojis. 0_0')

        row = await self.db.fetch_one('SELECT `id`, `nsfw`, `author_id` FROM `emojis` WHERE `name` LIKE :name', {'name': name})
        if row is None:
            await ctx.send(f':x: Emoji `{name}` not exists in bot.')
        else:
            if ctx.author.id == int(environ.get('OWNER_ID')) or int(row[2]) == ctx.author.id:
                if row[1]:
                    await self.db.execute('UPDATE `emojis` SET `nsfw` = 0 WHERE `id` = :id', {'id': row[0]})
                    await ctx.send(f':white_check_mark: Emoji `{name}` was **unmarked** as NSFW.')
                else:
                    await self.db.execute('UPDATE `emojis` SET `nsfw` = 1 WHERE `id` = :id', {'id': row[0]})
                    await ctx.send(f':white_check_mark: Emoji `{name}` was **marked** as NSFW.')
            else:
                await ctx.send(':x: Sorry, You can\'t mark other\'s emoji.')

    @commands.command(name='react', description='Reacts message with emoji.')
    async def cmd_react(self, ctx, emoji: str, message_id: int):
        try:
            msg = await ctx.fetch_message(message_id)
        except discord.errors.NotFound:
            await ctx.send(':x: Message not found or not from this channel.')
        else:
            row = await self.db.fetch_one('SELECT `id`, `nsfw` FROM `emojis` WHERE `name` LIKE :name', {'name': emoji})
            if row is None:
                await ctx.send(f':x: Emoji with name `{emoji}` not found in bot.')
            else:
                if row[2]:
                    await ctx.send(':x: You can\'t react message because your selected emoji was marked as **NSFW only**.')
                else:
                    await msg.add_reaction(self.bot.get_emoji(row[0]))


def setup(bot):
    bot.add_cog(Commands(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
