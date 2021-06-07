import logging
import time
import re
import requests
from os import environ
from math import ceil
import discord
from discord.ext import commands
from discord_components import Button
from discord_components import ButtonStyle


log = logging.getLogger(__name__)


def if_owner(ctx):
    if ctx.author.id == int(environ.get('OWNER_ID')):
        return True
    else:
        return False


class Commands(commands.Cog):
    """Commands cog for Discord Bot."""
    regex = re.compile(r'\\?<(a?)\\?:[\w_]{2,32}\\?:(\d{12,24})\\?>', re.ASCII)

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command()
    @commands.check(if_owner)
    async def reload(self, ctx, which: str = 'all'):
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

    @commands.command()
    async def ping(self, ctx):
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
        uptime = time.time() - self.bot.start_time
        time_d = int(uptime) / (3600 * 24)
        time_h = int(uptime) / 3600 - int(time_d) * 24
        time_min = int(uptime) / 60 - int(time_h) * 60 - int(time_d) * 24 * 60
        time_sec = int(uptime) - int(time_min) * 60 - int(time_h) * 3600 - int(time_d) * 24 * 60 * 60
        uptime_str = '%01d days, %02d hours, %02d minutes, %02d seconds' % (time_d, time_h, time_min, time_sec)
        embed.add_field(
            name=':hourglass: Bot\'s Uptime',
            value=uptime_str,
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def list(self, ctx, page: int = 1):
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
        await ctx.send(embed=embed, components=[buttons])

    @commands.command()
    async def add(self, ctx, name, emoji):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.send('Sorry, Webhooks and Bots can\'t add emojis to bot. 0_0')
        match = self.regex.match(emoji)
        if match is None:
            return await ctx.send(':x: That\'s not an emoji.')
        else:
            animated, emoji_id = match.groups()
        author = ctx.author.id
        row = await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` LIKE :name', {'name': name})
        if row is None:
            if animated:
                image = requests.get(f'https://cdn.discordapp.com/emojis/{emoji_id}.gif').content
                guild = await self.db.fetch_one('SELECT `id` FROM `guilds` WHERE `animated_usage` < 50 ORDER BY `created` LIMIT 1')
            else:
                image = requests.get(f'https://cdn.discordapp.com/emojis/{emoji_id}.png').content
                guild = await self.db.fetch_one('SELECT `id` FROM `guilds` WHERE `static_usage` < 50 ORDER BY `created` LIMIT 1')
            guild = self.bot.get_guild(guild[0])
            try:
                result = await guild.create_custom_emoji(
                    name=name, image=image,
                    reason=f'Addition Requested by {author}'
                )
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    await ctx.send(f':x: Bot have rate limited.\n`{e}`')
                    return
                else:
                    await ctx.send(f':x: Emoji was not added to bot.\n`{e}`')
                    return
            else:
                await self.db.execute(
                    'INSERT INTO `emojis` (`id`, `name`, `animated`, `author`, `guild`) VALUES (:id, :name, :animated, :author, :guild)',
                    {'id': result.id, 'name': result.name, 'animated': result.animated, 'author': author, 'guild': guild.id}
                )
                if animated:
                    await self.db.execute(
                        'UPDATE `guilds` SET `animated_usage` = `animated_usage` + 1 WHERE `id` = :guild',
                        {'guild': guild.id}
                    )
                else:
                    await self.db.execute(
                        'UPDATE `guilds` SET `static_usage` = `static_usage` + 1 WHERE `id` = :guild',
                        {'guild': guild.id}
                    )
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot.')
        else:
            await ctx.send(f':x: Name is already taken, try other name.')

    @commands.command()
    async def react(self, ctx, emoji: str, message_id: int):
        try:
            msg = await ctx.fetch_message(message_id)
        except discord.errors.NotFound:
            return await ctx.send(':x: Message not found or not from this channel.')
        else:
            row = await self.db.fetch_one(
                'SELECT `id` FROM `emojis` WHERE `name` LIKE :name',
                {'name': emoji}
            )
            if row is None:
                return await ctx.send(f':x: Emoji with name `{emoji}` not found in bot.')
            else:
                await msg.add_reaction(self.bot.get_emoji(row[0]))


def setup(bot):
    bot.add_cog(Commands(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
