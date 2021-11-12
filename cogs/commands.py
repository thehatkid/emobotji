from datetime import datetime
import logging
import yaml
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class CogCommands(commands.Cog):
    """Commands cog for Discord Bot."""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.db = bot.db

    @commands.command(name='reload', description='Reloads extenstion/cog (requires OWNER_ID)')
    @commands.check(lambda ctx: ctx.author.id in cfg['bot']['supervisors'])
    async def cmd_reload(self, ctx: commands.Context, which: str = 'all'):
        if which == 'all':
            self.bot.reload_extension('cogs.events')
            self.bot.reload_extension('cogs.commands')
            self.bot.reload_extension('cogs.categories.misc')
            self.bot.reload_extension('cogs.categories.listing')
            self.bot.reload_extension('cogs.categories.add')
            self.bot.reload_extension('cogs.categories.manage')
            self.bot.reload_extension('cogs.help')
            self.bot.reload_extension('cogs.emoji')
        elif which == 'events':
            self.bot.reload_extension('cogs.events')
        elif which == 'commands':
            self.bot.reload_extension('cogs.commands')
            self.bot.reload_extension('cogs.categories.misc')
            self.bot.reload_extension('cogs.categories.listing')
            self.bot.reload_extension('cogs.categories.add')
            self.bot.reload_extension('cogs.categories.manage')
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
        total_guilds = len(self.bot.guilds)
        total_users = 0
        for guild in self.bot.guilds:
            total_users += guild.member_count

        embed = disnake.Embed(title=':information_source: Bot Statistics', colour=disnake.Colour.blurple())
        embed.add_field(name=':hourglass: Bot uptime',value=uptime_str, inline=False)
        embed.add_field(
            name=':hourglass: Bot started since',
            value='<t:{0}:R>'.format(int(self.bot.start_time.timestamp())),
            inline=False
        )
        embed.add_field(name=':bar_chart: Servers joined', value=total_guilds, inline=False)
        embed.add_field(name=':bar_chart: Total users in servers', value=total_users, inline=False)
        embed.add_field(
            name=':bar_chart: Total emojis',
            value='{0} emojis *({1} SFW, {2} NSFW)*'.format(emojis[0], emojis[1], emojis[2]),
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CogCommands(bot))
    log.info(f'Loaded cog: {__name__}')


def teardown(bot):
    log.info(f'Unloaded cog: {__name__}')
