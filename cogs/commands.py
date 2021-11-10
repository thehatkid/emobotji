import asyncio
from datetime import datetime
from datetime import timedelta
from io import BytesIO
import logging
import re
import aiohttp
from os import environ
from math import ceil
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)

VIEW_EMOJIS = {
    # You can put your emoji into this dictonary for using somewhere... :/
    'next': disnake.PartialEmoji(
        name="page_next",
        animated=False,
        id=870595469536006154
    ),
    'prev': disnake.PartialEmoji(
        name="page_prev",
        animated=False,
        id=870595458010058782
    ),
    'close': disnake.PartialEmoji(
        name="page_close",
        animated=False,
        id=870595479505887303
    )
}


class ViewPaginator(disnake.ui.View):
    def __init__(self, author: disnake.User, embeds: list[disnake.Embed], entries: int, page: int = 0):
        """
        Parameters
        ----------
        author: :class:`~disnake.User`
            Discord User object.
        embeds: :class:`list[disnake.Embed]`
            Embeds for pagination.
        entries: :class:`int`
            Entries count for preview.
        page: :class:`int`
            Starting embed page.
        """
        super().__init__(timeout=120)
        self.author = author
        self.embeds = embeds
        self.entries = entries
        self.page = page

        # Set footer to first embed
        self.embeds[page].set_footer(text=f'Page {self.page + 1} of {len(self.embeds)} ({self.entries} entries)')

        # If have only one embed, disable all navigation buttons
        if len(self.embeds) <= 1:
            self.children[0].disabled = True
            self.children[1].disabled = True
        # If first page, disable "Previous" button
        elif self.page == 0:
            self.children[0].disabled = True
            self.children[1].disabled = False
        # If last page, disable "Next" button
        elif self.page == len(self.embeds) - 1:
            self.children[0].disabled = False
            self.children[1].disabled = True

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # If Sender's User ID is not equals with User ID from Interaction...
        if self.author.id != interaction.author.id:
            # Interaction checks fails
            await interaction.response.send_message(
                content=':x: You can\'t press buttons belong command sender.',
                ephemeral=True
            )
            return False
        # Interaction checks passes
        return True

    async def on_timeout(self):
        embed = disnake.Embed(
            title=':x: List was closed.',
            description='Reason: `Automatically closed due to inactivity.`',
            colour=disnake.Colour.dark_red()
        )
        await self.msg.edit(embed=embed, view=None)

    @disnake.ui.button(emoji=VIEW_EMOJIS['prev'], style=disnake.ButtonStyle.gray)
    async def page_prev(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.page == 0:
            await interaction.response.defer()
        else:
            self.page -= 1
            # If first page, disable "Previous" button
            if self.page == 0:
                self.children[0].disabled = True
                self.children[1].disabled = False
            # Else enable all navigation buttons
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = self.embeds[self.page]
            embed.set_footer(text=f'Page {self.page + 1} of {len(self.embeds)} ({self.entries} entries)')
            await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji=VIEW_EMOJIS['next'], style=disnake.ButtonStyle.gray)
    async def page_next(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.page == len(self.embeds) - 1:
            await interaction.response.defer()
        else:
            self.page += 1
            # If last page, disable "Next" button
            if self.page == len(self.embeds) - 1:
                self.children[0].disabled = False
                self.children[1].disabled = True
            # Else enable all navigation buttons
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = self.embeds[self.page]
            embed.set_footer(text=f'Page {self.page + 1} of {len(self.embeds)} ({self.entries} entries)')
            await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji=VIEW_EMOJIS['close'], style=disnake.ButtonStyle.red)
    async def page_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title=':x: List was closed.',
            description='Reason: `Closed by User.`',
            colour=disnake.Colour.dark_red()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()


class Commands(commands.Cog):
    """Commands cog for Discord Bot."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.http = aiohttp.ClientSession(
            loop=bot.loop, read_timeout=10,
            headers={'User-Agent': environ.get('USER_AGENT')}
        )
        self.REGEX_EMOJI = re.compile(
            r'\\?<(a?)\\?:[\w_]{2,32}\\?:(\d{12,24})\\?>',
            re.ASCII
        )

    def cog_unload(self):
        async def close_http_session():
            await self.http.close()
        self.bot.loop.create_task(close_http_session())

    @commands.command(name='q')
    async def cmd_testpages(self, ctx: commands.Context):
        embeds = [
            disnake.Embed(title='Test', description='One!'),
            disnake.Embed(title='Test', description='Two!'),
            disnake.Embed(title='Test', description='Three!'),
            disnake.Embed(title='Test', description='Four!'),
            disnake.Embed(title='Test', description='Five!')
        ]
        view = ViewPaginator(ctx.author, embeds, 55)
        view.msg = await ctx.send(embed=embeds[0], view=view)

    @commands.command(name='reload', description='Reloads extenstion/cog (requires OWNER_ID)')
    @commands.check(lambda ctx: ctx.author.id == int(environ.get('OWNER_ID')))
    async def cmd_reload(self, ctx: commands.Context, which: str = 'all'):
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

    @commands.command(name='ping', description='Shows embed with bot latency')
    async def cmd_ping(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':ping_pong: Pong!',
            colour=disnake.Colour.blurple()
        )
        embed.set_footer(
            text='Requested by {0}#{1}'.format(
                ctx.author.name, ctx.author.discriminator
            ),
            icon_url=ctx.author.avatar
        )
        embed.add_field(
            name=':signal_strength: Bot Latency',
            value='{}ms'.format(round(self.bot.latency * 1000)),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='statistics', description='Shows an embed with bot statistics', aliases=['stats', 'stat'])
    async def cmd_statistics(self, ctx: commands.Context):
        uptime = datetime.now().timestamp() - self.bot.start_time.timestamp()
        time_d = int(uptime) / (3600 * 24)
        time_h = int(uptime) / 3600 - int(time_d) * 24
        time_min = int(uptime) / 60 - int(time_h) * 60 - int(time_d) * 24 * 60
        time_sec = int(uptime) - int(time_min) * 60 - int(time_h) * 3600 - int(time_d) * 24 * 60 * 60
        uptime_str = '%01d days, %02d hours, %02d minutes, %02d seconds' % (time_d, time_h, time_min, time_sec)
        emojis = await self.db.fetch_one("""
        SELECT (
            SELECT COUNT(*) FROM `emojis`
        ) AS emojis_total,
        (
            SELECT COUNT(*) FROM `emojis` WHERE `nsfw` = 0
        ) AS emojis_total_sfw,
        (
            SELECT COUNT(*) FROM `emojis` WHERE `nsfw` = 1
        ) AS emojis_total_nsfw
        """)

        embed = disnake.Embed(title=':information_source: Bot Statistics', colour=disnake.Colour.blurple())
        embed.add_field(
            name=':hourglass: Bot Uptime',
            value='{0}\n*(up at <t:{1}:f>)*'.format(uptime_str, int(self.bot.start_time.timestamp())),
            inline=False
        )
        embed.add_field(
            name=':hourglass: Bot Last Restart',
            value='<t:{0}:R>'.format(int(self.bot.start_time.timestamp())),
            inline=False
        )
        embed.add_field(
            name=':bar_chart: Guilds Joined',
            value='{0} guilds'.format(len(self.bot.guilds)),
            inline=False
        )
        embed.add_field(
            name=':bar_chart: Total Emojis on Bot',
            value='{0} emojis *({1} SFW, {2} NSFW)*'.format(emojis[0], emojis[1], emojis[2]),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='list', description='Shows an embed with emoji list')
    async def cmd_list(self, ctx: commands.Context, page: int = 1):
        if isinstance(ctx.channel, disnake.DMChannel):
            NSFW = False
        else:
            NSFW = True if ctx.channel.is_nsfw() else False

        if NSFW:
            EMOJI_LIST = await self.db.fetch_all('SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` ORDER BY `name` ASC')
        else:
            EMOJI_LIST = await self.db.fetch_all('SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `nsfw` = 0 ORDER BY `name` ASC')

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
            EMOJI_LIST = await self.db.fetch_all(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name ORDER BY `name` ASC',
                {'name': f'%{name}%'}
            )
        else:
            EMOJI_LIST = await self.db.fetch_all(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` LIKE :name AND `nsfw` = 0 ORDER BY `name` ASC',
                {'name': f'%{name}%'}
            )

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

    @commands.command(name='info', description='Shows an embed with emoji infomation by name. Who created, when emoji was uploaded, etc.')
    async def cmd_info(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if ctx.channel.is_nsfw() else False
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        row = await self.db.fetch_one('SELECT `id`, `name`, `animated`, `nsfw`, `author_id`, `created` FROM `emojis` WHERE `name` = :name', {'name': name})
        if row is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot.', mention_author=False)
        else:
            embed = disnake.Embed(
                title=f':information_source: Emoji `{name}`',
                colour=disnake.Colour.blurple()
            )

            if not is_nsfw and row[3]:
                embed.description = '*Preview of Emoji are unavailable because that\'s NSFW*'
            else:
                embed.set_image(url='https://cdn.discordapp.com/emojis/{0}.{1}'.format(row[0], 'gif' if row[2] else 'png'))

            embed.add_field(name='Uploaded by:', value='<@{0}>{1}'.format(row[4], ' *(is you!)*' if int(row[4]) == ctx.author.id else ''), inline=False)
            embed.add_field(name='Created at:', value='<t:{0}:f> (<t:{0}:R>)'.format(int((row[5] + timedelta(hours=7)).timestamp())), inline=False)
            embed.add_field(name='Animated?', value='Yes' if row[2] else 'No', inline=False)
            embed.add_field(name='NSFW?', value='Yes' if row[3] else 'No', inline=False)
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='big', description='Posts full-sized image of emoji.')
    async def cmd_big(self, ctx: commands.Context, name: str):
        if isinstance(ctx.channel, disnake.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if ctx.channel.is_nsfw() else False
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        row = await self.db.fetch_one('SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` = :name', {'name': name})
        if row is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot.', mention_author=False)
        else:
            if not is_nsfw and row[3]:
                await ctx.reply(':x: Emoji are unavailable for posting here because that\'s **NSFW**.', mention_author=False)
            else:
                image_format = 'gif' if row[2] else 'png'
                url = 'https://cdn.discordapp.com/emojis/{0}.{1}'.format(row[0], image_format)
                async with self.http.get(url) as response:
                    image = BytesIO(await response.read())
                await ctx.send(
                    content='<{0}:{1}:{2}>'.format('a' if row[2] else '', row[1], row[0]),
                    file=disnake.File(fp=image, filename='{0}.{1}'.format(row[1], image_format))
                )

    @commands.command(name='add', description='Adds custom emoji.')
    async def cmd_add(self, ctx: commands.Context, name: str, emoji: str, is_nsfw: str = '0'):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.reply(':x: Sorry, Webhooks and Bots can\'t add emojis to bot. 0_0')
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        if await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` = :name', {'name': name}):
            return await ctx.reply(f':x: `{name}` is already taken, try other name.', mention_author=False)
        if is_nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'y', 'true', '18+']:
            is_nsfw = True
        else:
            is_nsfw = False

        match = self.REGEX_EMOJI.match(emoji)
        if match is None:
            return await ctx.reply(f':x: `{emoji}`: That\'s not an emoji.', mention_author=False)
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
            return await ctx.reply(':x: Emoji was not uploaded: `NO_AVAILABLE_GUILDS`', mention_author=False)
        guild = self.bot.get_guild(guild[0])

        try:
            result = await guild.create_custom_emoji(
                name=name, image=image,
                reason=f'Addition Requested by {author}'
            )
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                await ctx.reply(f':x: Bot have rate limited.\n`{e}`', mention_author=False)
            await ctx.reply(f':x: Emoji was not added to bot.\n`{e}`', mention_author=False)
        else:
            await self.db.execute(
                'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `created`, `author_id`, `guild_id`) VALUES (:id, :name, :animated, :nsfw, :created, :author_id, :guild_id)',
                {'id': result.id, 'name': result.name, 'animated': result.animated, 'nsfw': is_nsfw, 'created': datetime.utcnow(), 'author_id': author, 'guild_id': guild.id}
            )
            if animated:
                await self.db.execute('UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            else:
                await self.db.execute('UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            if is_nsfw:
                await ctx.reply(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage.', mention_author=False)
            else:
                await ctx.reply(f':white_check_mark: Emoji {result} was added to bot.', mention_author=False)

    @commands.command(name='add-from-url', description='Adds emoji from URL with Image.')
    async def cmd_addfromurl(self, ctx: commands.Context, name: str, url: str, is_nsfw: str = '0'):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.reply(':x: Sorry, Webhooks and Bots can\'t add emojis to bot. 0_0', mention_author=False)
        if not re.fullmatch(r'\w{2,32}', name, re.ASCII):
            return await ctx.reply(f':x: `{name}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.', mention_author=False)
        if await self.db.fetch_one('SELECT `name` FROM `emojis` WHERE `name` = :name', {'name': name}):
            return await ctx.reply(f':x: `{name}` is already taken, try other name.', mention_author=False)
        if is_nsfw in ['is-nsfw', 'is_nsfw', 'isnsfw', 'nsfw', '1', 'yes', 'y', 'true', '18+']:
            is_nsfw = True
        else:
            is_nsfw = False

        author = ctx.author.id

        try:
            async with self.http.get(url) as response:
                if response.status == 200:
                    if response.headers['content-type'] not in {'image/png', 'image/jpeg', 'image/gif'}:
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
            result = await guild.create_custom_emoji(
                name=name, image=image,
                reason=f'Addition Requested by {author}'
            )
        except disnake.errors.HTTPException as e:
            if e.status == 429:
                return await ctx.reply(f':x: Bot have rate limited.\n`{e}`', mention_author=False)
            await ctx.reply(f':x: Emoji was not added to bot.\n`{e}`', mention_author=False)
        else:
            await self.db.execute(
                'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `created`, `author_id`, `guild_id`) VALUES (:id, :name, :animated, :nsfw, :created, :author_id, :guild_id)',
                {'id': result.id, 'name': result.name, 'animated': result.animated, 'nsfw': is_nsfw, 'created': datetime.utcnow(), 'author_id': author, 'guild_id': guild.id}
            )
            if animated:
                await self.db.execute('UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            else:
                await self.db.execute('UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = :guild_id', {'guild_id': guild.id})
            if is_nsfw:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot and **marked as NSFW** only usage.', mention_author=False)
            else:
                await ctx.send(f':white_check_mark: Emoji {result} was added to bot.', mention_author=False)

    @commands.command(name='mark-nsfw', description='Marks emoji as NSFW usage only, also unmarks if was marked.', aliases=['nsfw', 'is-nsfw', 'toggle-nsfw'])
    async def cmd_marknsfw(self, ctx: commands.Context, name: str):
        if ctx.message.webhook_id or ctx.author.bot:
            return await ctx.send(":x: Sorry, Webhooks and Bots can't mark emojis. 0_0")

        row = await self.db.fetch_one('SELECT `id`, `nsfw`, `author_id` FROM `emojis` WHERE `name` = :name', {'name': name})
        if row is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot.', mention_author=False)
        else:
            if ctx.author.id == int(environ.get('OWNER_ID')) or int(row[2]) == ctx.author.id:
                if row[1]:
                    await self.db.execute('UPDATE `emojis` SET `nsfw` = 0 WHERE `id` = :id', {'id': row[0]})
                    await ctx.reply(f':white_check_mark: Emoji `{name}` was **unmarked** as NSFW.', mention_author=False)
                else:
                    await self.db.execute('UPDATE `emojis` SET `nsfw` = 1 WHERE `id` = :id', {'id': row[0]})
                    await ctx.reply(f':white_check_mark: Emoji `{name}` was **marked** as NSFW.', mention_author=False)
            else:
                await ctx.reply(':x: Sorry, You can\'t mark other\'s emoji.', mention_author=False)

    @commands.command(name='react', description='Reacts message with emoji.')
    async def cmd_react(self, ctx: commands.Context, emoji: str, message_id: int):
        try:
            msg = await ctx.fetch_message(message_id)
        except disnake.errors.NotFound:
            await ctx.reply(':x: Message not found or not from this channel.', mention_author=False)
        else:
            row = await self.db.fetch_one('SELECT `id`, `nsfw` FROM `emojis` WHERE `name` = :name', {'name': emoji})
            if row is None:
                await ctx.reply(f':x: Emoji with name `{emoji}` not found in bot.', mention_author=False)
            else:
                if row[1]:
                    await ctx.reply(':x: You can\'t react message because your selected emoji was marked as **NSFW only**.', mention_author=False)
                else:
                    await msg.add_reaction(self.bot.get_emoji(row[0]))


def setup(bot):
    bot.add_cog(Commands(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
