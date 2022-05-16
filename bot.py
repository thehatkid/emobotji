import logging
import yaml
from datetime import datetime
from utils.database import Database
from utils.help import HelpCommand
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
    message_content=True,
    messages=True,
    guild_messages=True,
    dm_messages=True
)

# Initialize Bot Class
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(cfg['bot']['prefix']),
    help_command=HelpCommand(),
    intents=intents,
    allowed_mentions=disnake.AllowedMentions(
        everyone=False,
        users=True,
        roles=False,
        replied_user=False
    ),
    status=disnake.Status.online,
    activity=disnake.Activity(
        type=disnake.ActivityType.playing,
        name=f'with Emojis | Help: {cfg["bot"]["prefix"]}help'
    ),
    sync_commands=True,
    sync_commands_debug=True
)
# Connect MySQL Database
bot.db = Database(
    host=cfg['mysql']['host'],
    port=cfg['mysql']['port'],
    user=cfg['mysql']['user'],
    password=cfg['mysql']['password'],
    database=cfg['mysql']['database']
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
bot.load_extension('cogs.emoji')
bot.load_extensions('cogs/app_commands')
bot.load_extensions('cogs/text_commands')

# Running Bot from Bot Token
bot.run(cfg['bot']['token'])
