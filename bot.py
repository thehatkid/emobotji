import logging
import time
from os import environ
from dotenv import load_dotenv
from databases import Database
import discord
from discord.ext import commands
from discord_components import DiscordComponents


# Setting up Logging
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
    level=logging.INFO
)
log = logging.getLogger('bot')

# Loads Predefined Environment Variables
load_dotenv()

# Connect MySQL Database
database = Database(
    'mysql://{0}:{1}@{2}:{3}/{4}'.format(
        environ.get('MYSQL_USER'),
        environ.get('MYSQL_PASSWORD'),
        environ.get('MYSQL_HOST'),
        environ.get('MYSQL_PORT'),
        environ.get('MYSQL_DATABASE')
    )
)

if not environ.get('BOT_TOKEN'):
    log.error('No Environment Variable for Bot Token. (BOT_TOKEN)')
    exit()

log.info('Starting discord.py {0} {1}...'.format(
    discord.__version__, discord.version_info.releaselevel
))

# Initialize Bot Class
bot = commands.Bot(command_prefix=environ.get('BOT_PREFIX'), help_command=None)
DiscordComponents(bot)
bot.db = database
bot.start_time = time.time()

# After bot ready actions
async def after_bot_ready():
    await bot.wait_until_ready()
    await bot.db.connect()
    DiscordComponents(bot)

# Bot's Activity
async def bot_activities():
    game = discord.Game('with emojis | prefix: {0}'.format(environ.get('BOT_PREFIX')))
    await bot.wait_until_ready()
    await bot.change_presence(activity=game, status=discord.Status.online)

bot.loop.create_task(after_bot_ready())
bot.loop.create_task(bot_activities())

# Loading Cogs
bot.load_extension('cogs.events')
bot.load_extension('cogs.commands')
bot.load_extension('cogs.help')
bot.load_extension('cogs.emoji')

# Running Bot from Bot Token
bot.run(environ.get('BOT_TOKEN'))
