import logging
import yaml
from disnake.ext import commands


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


def setup(bot):
    bot.add_cog(CogCommandsManage(bot))
    log.info('Loaded cog.')


def teardown(bot):
    log.info('Unloaded cog.')
