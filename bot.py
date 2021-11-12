import logging
import yaml
from datetime import datetime
from databases import Database
import disnake
from disnake.ext import commands

# Setting up Logging
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
    level=logging.INFO
)
log = logging.getLogger('bot')

# Load configurations
cfg = yaml.safe_load(open('config.yml', 'r'))

log.info('Starting disnake {0} {1}...'.format(
    disnake.__version__, disnake.version_info.releaselevel
))

intents = disnake.Intents(
    guilds=True,
    messages=True,
    guild_messages=True,
    dm_messages=True
)

# Initialize Bot Class
bot = commands.Bot(
    command_prefix=cfg['bot']['prefix'],
    help_command=None,
    intents=intents,
    status=disnake.Status.online,
    activity=disnake.Activity(
        type=disnake.ActivityType.playing,
        name=f'with Emojis | Help: {cfg["bot"]["prefix"]}help'
    )
)
# Connect MySQL Database
bot.db = Database(
    'mysql://{0}:{1}@{2}:{3}/{4}'.format(
        cfg['mysql']['user'],
        cfg['mysql']['password'],
        cfg['mysql']['host'],
        cfg['mysql']['port'],
        cfg['mysql']['database']
    )
)
# Bot start time for uptime stats
bot.start_time = datetime.now()

# After bot ready actions
async def after_bot_ready():
    await bot.wait_until_ready()
    # Connect Database
    await bot.db.connect()

bot.loop.create_task(after_bot_ready())

# Loading Cogs
bot.load_extension('cogs.events')
bot.load_extension('cogs.commands')
bot.load_extension('cogs.categories.misc')
bot.load_extension('cogs.categories.listing')
bot.load_extension('cogs.categories.add')
bot.load_extension('cogs.categories.manage')
bot.load_extension('cogs.help')
bot.load_extension('cogs.emoji')

# Running Bot from Bot Token
bot.run(cfg['bot']['token'])
