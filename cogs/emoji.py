import logging
import re
from discord.ext import commands


log = logging.getLogger(__name__)


class Emoji(commands.Cog):
    """Emoji cog for Discord Bot."""
    regex = re.compile(
        r'(?!<:)<?(;|:)([\w_]{2,32})(?!:\d+>)\1(?:\d+>)?',
        re.ASCII
    )

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.replies = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        emojis = await self.emojis(message.content)
        if emojis:
            self.replies[message.id] = await message.channel.send(emojis)

    @commands.Cog.listener()
    async def on_message_edit(self, _, after):
        if after.id not in self.replies:
            return
        emojis = await self.emojis(after.content)
        reply = self.replies[after.id]
        if not emojis:
            return await self.replies.pop(after.id).delete()
        elif emojis == reply.content:
            return
        else:
            await reply.edit(content=emojis)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            await self.replies.pop(message.id).delete()
        except KeyError:
            pass

    async def emojis(self, message: str):
        """
        Returns string with emoji(s).

        Parameters:
            message (str): Message text for filtering emojis.

        Returns:
            String with emojis for message.
            If not found returns nothing (empty string)
        """
        names = []
        for match in self.regex.finditer(message):
            try:
                names.append(match.group(2))
            except IndexError:
                pass
        if not names:
            return
        emojis = []
        for name in names:
            emojis.append(await self.get_formatted(name))
        if not emojis:
            return
        return ''.join(emojis)

    async def get_formatted(self, name):
        """
        Returns formatted emoji for Discord message.

        Parameters:
            name (str): Name of emoji to get and format it.

        Returns:
            String of formatted emoji for message:
                <a:emoji_name:emoji_id> (animated emoji)
                or
                <:emoji_name:emoji_id> (not animated emoji)
            If not found returns nothing (empty string)
        """
        row = await self.db.fetch_one(
            'SELECT `id`, `name`, `animated` FROM `emojis` WHERE `name` LIKE :name',
            values={'name': name}
        )
        if row:
            return '<{0}:{1}:{2}>'.format(
                'a' if row[2] else '',
                row[1],
                row[0]
            )
        else:
            return ''


def setup(bot):
    bot.add_cog(Emoji(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
