import logging
import yaml
import re
from utils.database import Database
from utils.views import ViewConfirmation
import disnake
from disnake import Option
from disnake import OptionType
from disnake.ext import commands

logger = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class AppCmdsManage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.slash_command(
        name='manage',
        description='Commands for emojis management'
    )
    async def scmd_manage(self, inter: disnake.AppCmdInter):
        pass

    @scmd_manage.sub_command(
        name='rename',
        description='Renames emoji\'s name to new name',
        options=[
            Option('emoji_name', 'The emoji for renaming', OptionType.string, True),
            Option('new_name', 'The new other name of emoji for renaming', OptionType.string, True)
        ]
    )
    async def scmd_manage_rename(self, inter: disnake.AppCmdInter, emoji_name: str, new_name: str):
        emoji_row = await self.db.get_emoji(emoji_name)

        if emoji_row is None:
            return await inter.response.send_message(
                f':x: Emoji with name `{emoji_name}` was not found in Bot',
                ephemeral=True
            )

        if inter.author.id not in cfg['bot']['supervisors']:
            if inter.author.id != emoji_row['author_id']:
                return await inter.response.send_message(
                    ':x: That\'s not your emoji for renaming it.',
                    ephemeral=True
                )

        if emoji_row['name'] == new_name:
            return await inter.response.send_message(
                ':x: The new name is same old name of emoji. Nothing to do.',
                ephemeral=True
            )

        if not re.fullmatch(r'\w{2,32}', new_name, re.ASCII):
            return await inter.response.send_message(
                f':x: `{new_name}` is not a valid emoji name to rename; use 2–32 English letters, numbers and underscores.',
                ephemeral=True
            )

        guild = self.bot.get_guild(emoji_row['guild_id'])

        try:
            emoji = await guild.fetch_emoji(emoji_row['id'])
        except disnake.HTTPException as e:
            return await inter.response.send_message(
                f':x: `{emoji_name}` was not found in Bot\'s servers. Please contact to Bot Developer.',
                ephemeral=True
            )

        view = ViewConfirmation(inter.author)
        await inter.response.send_message(
            f'Do You really want to rename emoji\'s name to `{new_name}`?',
            view=view
        )
        await view.wait()

        if view.switch is None:
            await inter.edit_original_message(
                content=':x: Cancelled due to inactivity.',
                view=None
            )
        elif view.switch is True:
            await inter.edit_original_message(
                content='Renaming...',
                view=None
            )

            try:
                new_emoji = await emoji.edit(name=new_name, reason=f'Renamed by {inter.author.id}')
            except Exception as e:
                await inter.edit_original_message(
                    content=f':x: Emoji deletion was failed by Discord Error. Please contact to Bot Developer.\nError: `{e}`'
                )
            else:
                await self.db.rename_emoji(new_emoji.id, new_emoji.name)

                await inter.edit_original_message(
                    content=f':white_check_mark: Emoji {new_emoji} was renamed to `{new_emoji.name}`!'
                )
        else:
            await inter.edit_original_message(
                content=':x: Cancelled by user.',
                view=None
            )

    @scmd_manage.sub_command(
        name='delete',
        description='Deletes emoji from bot',
        options=[
            Option('emoji_name', 'The emoji for deleting from bot', OptionType.string, True)
        ]
    )
    async def scmd_manage_delete(self, inter: disnake.AppCmdInter, emoji_name: str):
        emoji_row = await self.db.get_emoji(emoji_name)

        if emoji_row is None:
            return await inter.response.send_message(
                f':x: Emoji with name `{emoji_name}` was not found in Bot',
                ephemeral=True
            )

        if inter.author.id not in cfg['bot']['supervisors']:
            if inter.author.id != emoji_row['author_id']:
                return await inter.response.send_message(
                    ':x: That\'s not your emoji for deleting it.',
                    ephemeral=True
                )

        guild = self.bot.get_guild(emoji_row['guild_id'])

        try:
            emoji = await guild.fetch_emoji(emoji_row['id'])
        except disnake.HTTPException as e:
            return await inter.response.send_message(
                f':x: `{emoji_name}` was not found in Bot\'s servers. Please contact to Bot Developer.',
                ephemeral=True
            )

        view = ViewConfirmation(inter.author)
        await inter.response.send_message(
            f'Do You really want to delete {emoji} emoji?',
            view=view
        )
        await view.wait()

        if view.switch is None:
            await inter.edit_original_message(
                content=':x: Cancelled due to inactivity.',
                view=None
            )
        elif view.switch is True:
            await inter.edit_original_message(
                content='Deleting...',
                view=None
            )

            try:
                await emoji.delete(reason=f'Deleted by {inter.author.id}')
            except disnake.HTTPException as e:
                await inter.edit_original_message(
                    content=f':x: Emoji deletion was failed by Discord Error. Please contact to Bot Developer.\nError: `{e}`'
                )
            else:
                await self.db.delete_emoji(emoji.id)

                if emoji.animated:
                    await self.db.decrease_usage_guild(emoji.guild_id, 'animated')
                else:
                    await self.db.decrease_usage_guild(emoji.guild_id, 'static')

                await inter.edit_original_message(
                    content=f':white_check_mark: Emoji `{emoji.name}` was deleted from bot!'
                )
        else:
            await inter.edit_original_message(
                content=':x: Cancelled by user.',
                view=None
            )

    @scmd_manage_rename.autocomplete('emoji_name')
    @scmd_manage_delete.autocomplete('emoji_name')
    async def autocomp_emojis(self, inter: disnake.AppCmdInter, name: str) -> list[str]:
        emoji_list = await self.db.get_emoji_list_by_name(name, inter.channel.is_nsfw)
        result = []

        for emoji in emoji_list:
            if len(result) < 25:
                if emoji[4] == inter.author.id:
                    result.append(emoji[1])
                else:
                    continue
            else:
                break

        return result


def setup(bot: commands.Bot):
    cog = AppCmdsManage(bot)
    bot.add_cog(cog)
    logger.info('Loaded')


def teardown(bot):
    logger.info('Unloaded')
