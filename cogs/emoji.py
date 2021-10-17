import logging
import re
import discord
from discord.ext import commands


log = logging.getLogger(__name__)


class Emoji(commands.Cog):
    """Message Event Handling cog for Discord Bot."""

    regex = re.compile(
        r'(?!<:)<?(;|:)([\w_]{2,32})(?!:\d+>)\1(?:\d+>)?',
        re.ASCII
    )

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.replies = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if message.channel.is_nsfw() else False

        emojis = await self.parse_emojis(message.content, is_nsfw)
        if emojis:
            self.replies[message.id] = await message.channel.send(emojis)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        if after.id not in self.replies:
            return
        reply = self.replies[after.id]

        if isinstance(after.channel, discord.DMChannel):
            is_nsfw = False
        else:
            is_nsfw = True if after.channel.is_nsfw() else False

        emojis = await self.parse_emojis(after.content, is_nsfw)
        if not emojis:
            return await self.replies.pop(after.id).delete()
        if emojis == await self.parse_emojis(before.content, is_nsfw):
            return
        await reply.edit(content=emojis)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
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
        emojis = []
        for match in self.regex.finditer(message):
            emojis.append(await self.emoji_get(match.group(2), nsfw))
        if not emojis:
            return None
        return ''.join(emojis)

    async def emoji_get(self, name: str, nsfw: bool) -> str:
        """
        Getting a emoji from Database and returns formatted emoji for Discord message if was been found.

        Parameters:
        -----------
        name: :class:`str`
            Name of emoji to get and format it.
        nsfw: :class:`bool`
            If True will return SFW and NSFW emoji, otherwise only SFW.

        Returns:
        --------
        :class:`str`
            String of formatted emoji for message:
                `<a:emoji_name:emoji_id>` (animated emoji)

                or

                `<:emoji_name:emoji_id>` (not animated emoji)

            If not found or emoji are NSFW but parameter `nsfw` are False returns nothing (empty string)
        """
        row = await self.db.fetch_one(
            'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` = :name',
            values={'name': name}
        )
        if row:
            if nsfw is False and row[3] == 1:
                return ''
            return '<{0}:{1}:{2}>'.format('a' if row[2] else '', row[1], row[0])
        return ''


def setup(bot):
    bot.add_cog(Emoji(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
