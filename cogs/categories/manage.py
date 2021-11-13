import logging
import yaml
import re
import disnake
from disnake.ext import commands
from utils.views import ViewConfirmation


log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class CogCommandsManage(commands.Cog):
    """Emojis management commands category."""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.db = bot.db

    @commands.command(name='mark-nsfw', description='Marks emoji as NSFW usage only, also unmarks if was marked.', aliases=['nsfw', 'is-nsfw', 'toggle-nsfw'])
    async def cmd_marknsfw(self, ctx: commands.Context, name: str):
        row = await self.db.fetch_one('SELECT `id`, `nsfw`, `author_id` FROM `emojis` WHERE `name` = :name', {'name': name})
        if row is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot.', mention_author=False)
        else:
            if ctx.author.id in cfg['bot']['supervisors'] or int(row[2]) == ctx.author.id:
                if row[1]:
                    await self.db.execute('UPDATE `emojis` SET `nsfw` = 0 WHERE `id` = :id', {'id': row[0]})
                    await ctx.reply(f':white_check_mark: Emoji `{name}` was **unmarked** as NSFW.', mention_author=False)
                else:
                    await self.db.execute('UPDATE `emojis` SET `nsfw` = 1 WHERE `id` = :id', {'id': row[0]})
                    await ctx.reply(f':white_check_mark: Emoji `{name}` was **marked** as NSFW.', mention_author=False)
            else:
                await ctx.reply(':x: Sorry, You can\'t mark other\'s emoji.', mention_author=False)

    @commands.command(name='rename', description='Renames owner\'s emoji to other name.')
    async def cmd_rename(self, ctx: commands.Context, emoji_name: str, emoji_new_name: str):
        row = await self.db.fetch_one('SELECT `id`, `author_id`, `guild_id` FROM `emojis` WHERE `name` = :name', {'name': emoji_name})
        if row is None:
            return await ctx.reply(f':x: Emoji with name `{emoji_name}` not found in bot.', mention_author=False)
        if ctx.author.id not in cfg['bot']['supervisors']:
            if ctx.author.id != row[1]:
                return await ctx.reply(':x: That\'s not your emoji for renaming it.', mention_author=False)
        if emoji_name == emoji_new_name:
            return await ctx.reply(':x: Same new name with old name. Nothing to do.', mention_author=False)
        if not re.fullmatch(r'\w{2,32}', emoji_new_name, re.ASCII):
            return await ctx.reply(f':x: `{emoji_new_name}` is not a valid emoji name to rename; use 2–32 English letters, numbers and underscores.', mention_author=False)

        guild = self.bot.get_guild(row[2])
        emoji = await guild.fetch_emoji(row[0])

        if emoji:
            view = ViewConfirmation(ctx.author)
            reply = await ctx.send(f'Do you want really rename to `{emoji_new_name}`?', view=view)
            await view.wait()
            if view.switch is None:
                await reply.edit(content=':x: Cancelled due to inactivity.', view=None)
            elif view.switch is True:
                await reply.edit(content='Processing...', view=None)
                try:
                    new_emoji = await emoji.edit(name=emoji_new_name, reason=f'Renamed by {ctx.author.id}')
                except Exception as e:
                    await reply.edit(content=f':x: Emoji renaming was failed by Discord Error. Please contact to Bot Developer.\n{e}')
                else:
                    await self.db.execute(
                        'UPDATE `emojis` SET `name` = :new_name WHERE `id` = :id',
                        {'new_name': new_emoji.name, 'id': new_emoji.id}
                    )
                    await reply.edit(content=f':white_check_mark: Emoji {new_emoji} was renamed to `{new_emoji.name}`!')
            else:
                await reply.edit(content=':x: Cancelled.', view=None)
        else:
            await ctx.send(f':x: {emoji_name} was not found in bot\'s servers. Please contact to Bot Developer.')


def setup(bot):
    bot.add_cog(CogCommandsManage(bot))
    log.info('Loaded cog.')


def teardown(bot):
    log.info('Unloaded cog.')
