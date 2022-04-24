import logging
from utils.database import Database
from thefuzz import process
import disnake
from disnake import Option
from disnake import OptionType
from disnake.ext import commands

logger = logging.getLogger(__name__)


class AppCmdsEmoji(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.slash_command(
        name='emoji',
        description='Emoji command to post the emoji by name',
        options=[
            Option('emoji', 'The emoji name to post the emoji with that name', OptionType.string, True)
        ]
    )
    async def scmd_emoji(self, inter: disnake.AppCmdInter, emoji: str):
        emoji_row = await self.db.get_emoji(emoji)

        if emoji_row:
            if emoji_row['nsfw'] and not inter.channel.nsfw:
                await inter.response.send_message(
                    ':x: You can\'t post this emoji because it\'s **NSFW usage** only',
                    ephemeral=True
                )
            else:
                await inter.response.send_message(emoji_row['formatted'])
        else:
            await inter.response.send_message(
                f':x: Emoji with name `{emoji}` was not found',
                ephemeral=True
            )

    @commands.slash_command(
        name='react',
        description='Reacts the message with bot\'s emoji by Message ID',
        options=[
            Option('emoji', 'The emoji name to react the emoji to message', OptionType.string, True),
            Option('message_id', 'The message ID from same channel to react it', OptionType.string, True)
        ]
    )
    async def scmd_react(self, inter: disnake.AppCmdInter, emoji: str, message_id: str):
        emoji_row = await self.db.get_emoji(emoji)

        try:
            message_id = int(message_id)
        except ValueError:
            return await inter.response.send_message(':x: The message ID invalid.', ephemeral=True)

        if emoji_row:
            if emoji_row['nsfw'] and not inter.channel.nsfw:
                await inter.response.send_message(
                    ':x: You can\'t react this message with that emoji because it\'s **NSFW usage** only',
                    ephemeral=True
                )
            else:
                message = inter.channel.get_partial_message(message_id)

                if not message:
                    return await inter.response.send_message(
                        ':x: The message was not found in this channel.',
                        ephemeral=True
                    )

                try:
                    await message.add_reaction(emoji_row['formatted'])
                except disnake.HTTPException as e:
                    await inter.response.send_message(
                        f':x: Failed to react this message with emoji.\nError: `{e}`',
                        ephemeral=True
                    )
                else:
                    await inter.response.send_message(
                        f':white_check_mark: Successfully reacted the message with {emoji_row["formatted"]}',
                        ephemeral=True
                    )
        else:
            await inter.response.send_message(
                f':x: Emoji with name `{emoji}` was not found in Bot',
                ephemeral=True
            )

    @scmd_emoji.autocomplete('emoji')
    @scmd_react.autocomplete('emoji')
    async def autocomp_emojis(self, inter: disnake.AppCmdInter, name: str) -> list[str]:
        emoji_list = await self.db.get_emoji_list(inter.channel.nsfw)
        emoji_names = [emoji[1] for emoji in emoji_list]

        if name:
            matches = process.extract(name, emoji_names, limit=25)
            result = [match[0] for match in matches]
        else:
            result = []
            for name in emoji_names:
                if len(result) < 25:
                    result.append(name)
                else:
                    break

        return result


def setup(bot: commands.Bot):
    cog = AppCmdsEmoji(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
