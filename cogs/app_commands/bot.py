import logging
import yaml
import os
import psutil
from datetime import datetime
from utils import human_readable_size
from utils.database import Database
import disnake
from disnake.ext import commands

logger = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class AppCmdsBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db
        self.INVITE_BOT_URL = cfg['bot']['misc']['invite-bot']
        self.INVITE_SERVER_URL = cfg['bot']['misc']['invite-server']

    @commands.slash_command(
        name='bot',
        description='Bot\'s commands'
    )
    async def scmd_bot(self, inter: disnake.AppCmdInter):
        pass

    @scmd_bot.sub_command(
        name='ping',
        description='Pings the bot and shows ping latency'
    )
    async def scmd_bot_ping(self, inter: disnake.AppCmdInter):
        embed = disnake.Embed(
            title=':ping_pong: Pong!',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name=':signal_strength: Bot Latency',
            value='{}ms'.format(round(self.bot.latency * 1000)),
            inline=False
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @scmd_bot.sub_command(
        name='statistics',
        description='Shows an embed with bot statistics'
    )
    async def scmd_bot_statistics(self, inter: disnake.AppCmdInter):
        uptime = datetime.now().timestamp() - self.bot.start_time.timestamp()
        time_d = int(uptime) / (3600 * 24)
        time_h = int(uptime) / 3600 - int(time_d) * 24
        time_min = int(uptime) / 60 - int(time_h) * 60 - int(time_d) * 24 * 60
        time_sec = int(uptime) - int(time_min) * 60 - int(time_h) * 3600 - int(time_d) * 24 * 60 * 60
        uptime_str = '%01d days, %02d hours, %02d minutes and %02d seconds' % (time_d, time_h, time_min, time_sec)
        emojis = await self.db.get_emojis_counts()
        process = psutil.Process(os.getpid())
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_used = human_readable_size(ram.used)
        ram_total = human_readable_size(ram.total)
        ram_available = human_readable_size(ram.available)
        total_guilds = len(self.bot.guilds)
        total_users = 0
        for guild in self.bot.guilds:
            total_users += guild.member_count

        embed = disnake.Embed(
            title=':information_source: Bot statistics',
            color=disnake.Color.blurple()
        )

        embed.add_field(
            name=':clock1: Bot Uptime',
            value=f'{uptime_str} (<t:{int(self.bot.start_time.timestamp())}:R>)',
            inline=False
        )
        embed.add_field(
            name=':page_facing_up: Process PID',
            value=process.pid,
            inline=True
        )
        embed.add_field(
            name=':control_knobs: CPU Usage',
            value=f'{cpu_percent}%',
            inline=True
        )
        embed.add_field(
            name=':file_cabinet: Bot RAM Usage',
            value=human_readable_size(process.memory_info().rss),
            inline=True
        )
        embed.add_field(
            name=':file_cabinet: Total RAM',
            value=f'Using: {ram_used} ({ram.percent}%) / {ram_total}\nAvailable: {ram_available} ({ram.available * 100 / ram.total:.1f}%)',
            inline=False
        )
        embed.add_field(
            name=':bar_chart: Total emojis',
            value='{0} emojis *({1} SFW, {2} NSFW)*'.format(
                emojis['total'], emojis['total_sfw'], emojis['total_nsfw']
            ),
            inline=False
        )
        embed.add_field(
            name=':signal_strength: Ping latency',
            value=f'{round(self.bot.latency * 1000)}ms',
            inline=True
        )
        embed.add_field(
            name=':homes: Servers joined',
            value=f'{total_guilds} servers',
            inline=True
        )
        embed.add_field(
            name=':busts_in_silhouette: Total users in servers',
            value=f'{total_users} users',
            inline=True
        )

        await inter.response.send_message(embed=embed)

    @scmd_bot.sub_command(
        name='invite',
        description='Shows Bot Invite link'
    )
    async def scmd_bot_invite(self, inter: disnake.AppCmdInter):
        if self.INVITE_BOT_URL:
            await inter.response.send_message(self.INVITE_BOT_URL, ephemeral=True)
        else:
            await inter.response.send_message(
                ':x: This subcommand is not available for this moment',
                ephemeral=True
            )

    @scmd_bot.sub_command(
        name='support',
        description='Shows Bot Support Server'
    )
    async def scmd_bot_support(self, inter: disnake.AppCmdInter):
        if self.INVITE_SERVER_URL:
            await inter.response.send_message(
                f'Need any help with bot? You can join to support server and ask question.\n{self.INVITE_SERVER_URL}',
                ephemeral=True
            )
        else:
            await inter.response.send_message(
                ':x: This subcommand is not available for this moment',
                ephemeral=True
            )


def setup(bot: commands.Bot):
    cog = AppCmdsBot(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
