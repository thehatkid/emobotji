import logging
import re
from thefuzz import process
from datetime import datetime
import calendar
import disnake
from utils.database import Database
from disnake import Option
from disnake import OptionType
from disnake.ext import commands

logger = logging.getLogger(__name__)


class AppCmdsMisc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.slash_command(
        name='info',
        description='Shows an embed with emoji infomation by name',
        options=[
            Option('emoji', 'The emoji name for retrieving information', OptionType.string, True)
        ]
    )
    async def scmd_info(self, inter: disnake.AppCmdInter, emoji: str):
        if not re.fullmatch(r'\w{2,32}', emoji, re.ASCII):
            return await inter.response.send_message(
                f':x: `{emoji}` is not a valid emoji name; use 2–32 English letters, numbers and underscores.',
                ephemeral=True
            )

        emoji_row = await self.db.get_emoji(emoji)

        if emoji_row is None:
            await inter.response.send_message(f':x: Emoji `{emoji_row}` not exists in bot.', ephemeral=True)
        else:
            created_at = datetime.fromtimestamp(calendar.timegm(emoji_row['created_at'].timetuple()))
            created_field = '<t:{0}:f> (<t:{0}:R>)'.format(int(created_at.timestamp()))
            uploader_field = '<@{0}>'.format(emoji_row['author_id'])

            if emoji_row['author_id'] == inter.author.id:
                uploader_field += ' *(is you!)*'

            embed = disnake.Embed(title=f':information_source: Emoji `{emoji_row["name"]}`', colour=disnake.Colour.blurple())

            if emoji_row['nsfw'] and not inter.channel.nsfw:
                embed.description = '*Preview of Emoji are unavailable because that\'s NSFW*'
            else:
                embed.set_image(url='https://cdn.discordapp.com/emojis/{0}.{1}?size=512'.format(
                    emoji_row['id'],
                    'gif' if emoji_row['animated'] else 'png'
                ))

            embed.add_field(name='Uploaded by:', value=uploader_field, inline=False)
            embed.add_field(name='Created at:', value=created_field, inline=False)
            embed.add_field(name='Animated?', value='Yes' if emoji_row['animated'] else 'No', inline=False)
            embed.add_field(name='NSFW?', value='Yes' if emoji_row['nsfw'] else 'No', inline=False)

            await inter.response.send_message(embed=embed)

    @scmd_info.autocomplete('emoji')
    async def autocomp_emojis(self, inter: disnake.AppCmdInter, name: str) -> list[str]:
        if isinstance(inter.channel, disnake.TextChannel):
            nsfw = inter.channel.nsfw
        else:
            nsfw = False

        emoji_list = await self.db.get_emoji_list(nsfw)
        emoji_names = [emoji[1] for emoji in emoji_list]

        if name:
            matches = process.extract(name, emoji_names, limit=25)
            result = [match[0] for match in matches]
        else:
            result = []
            for emoji_name in emoji_names:
                if len(result) < 25:
                    result.append(emoji_name)
                else:
                    break

        return result


def setup(bot: commands.Bot):
    cog = AppCmdsMisc(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
