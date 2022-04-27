import logging
import re
from utils.database import Database
import disnake
from disnake.ext import commands

log = logging.getLogger(__name__)


class CogEmoji(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db
        self.replies = {}
        self.REGEX = re.compile(r'(?!<:)<?(;|:)([\w_]{2,32})(?!:\d+>)\1(?:\d+>)?(\n?)', re.ASCII)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, disnake.TextChannel):
            is_nsfw = message.channel.nsfw
        else:
            is_nsfw = False

        emojis = await self.parse_emojis(message.content, is_nsfw)
        if emojis:
            self.replies[message.id] = await message.channel.send(emojis)

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author.bot:
            return

        if after.id not in self.replies:
            return
        reply = self.replies[after.id]

        if isinstance(after.channel, disnake.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = after.channel.nsfw

        emojis = await self.parse_emojis(after.content, is_nsfw)
        if not emojis:
            return await self.replies.pop(after.id).delete()
        if emojis == await self.parse_emojis(before.content, is_nsfw):
            return
        await reply.edit(content=emojis)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot:
            return

        if message.id in self.replies:
            try:
                await self.replies.pop(message.id).delete()
            except Exception:
                return

    async def parse_emojis(self, message: str, nsfw: bool) -> str:
        """
        Parses emoji(s) to find and returns string with emoji(s).

        Parameters:
        -----------
        message: :class:`str`
            Message text for filtering emojis.
        nsfw: :class:`bool`
            If False searchs SFW (Safe For Work) emojis, otherwise searchs SFW and NSFW emojis.

        Returns:
        --------
        :class:`str`
            String with emojis for message.
            If not found returns :class:`None`
        """
        inputs = [match.groups()[1:] for match in self.REGEX.finditer(message)]
        if not inputs:
            return None

        emojis = []
        for name, newline in inputs:
            emoji = await self.db.get_formatted_emoji(name, nsfw)
            if emoji is None:
                emoji = ''
            emojis.append(emoji)
            if newline:
                emojis.append('\n')
        if not emojis:
            return None

        return ''.join(emojis)


def setup(bot: commands.Bot):
    cog = CogEmoji(bot)
    bot.add_cog(cog)
    log.info('Loaded')


def teardown(bot):
    log.info('Unloaded')
