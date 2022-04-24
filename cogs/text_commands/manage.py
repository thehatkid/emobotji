import logging
import yaml
import re
from utils.database import Database
from utils.views import ViewConfirmation
from disnake.ext import commands

log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class TextCmdsManage(commands.Cog, name='Emoji Management'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = bot.db

    @commands.command(name='mark-nsfw', description='Marks emoji as NSFW usage only, also unmarks if was marked', aliases=['nsfw', 'is-nsfw', 'toggle-nsfw'])
    async def cmd_marknsfw(self, ctx: commands.Context, name: str):
        emoji = await self.db.get_emoji(name)

        if emoji is None:
            await ctx.reply(f':x: Emoji `{name}` not exists in bot')
        else:
            if ctx.author.id in cfg['bot']['supervisors'] or emoji['author_id'] == ctx.author.id:
                if emoji['nsfw']:
                    await self.db.set_nsfw_mark(emoji['id'], False)
                    await ctx.reply(f':white_check_mark: Emoji `{name}` was **unmarked** as NSFW')
                else:
                    await self.db.set_nsfw_mark(emoji['id'], True)
                    await ctx.reply(f':white_check_mark: Emoji `{name}` was **marked** as NSFW')
            else:
                await ctx.reply(':x: Sorry, You can\'t mark other\'s emoji')

    @commands.command(name='rename', description='Renames emoji to other name')
    async def cmd_rename(self, ctx: commands.Context, emoji_name: str, emoji_new_name: str):
        emoji = await self.db.get_emoji(emoji_name)

        if emoji is None:
            return await ctx.reply(f':x: Emoji with name `{emoji_name}` not found in bot')

        if ctx.author.id not in cfg['bot']['supervisors']:
            if ctx.author.id != emoji['author_id']:
                return await ctx.reply(':x: That\'s not your emoji for renaming it')

        if emoji['name'] == emoji_new_name:
            return await ctx.reply(':x: Same new name with old name. Nothing to do.')

        if not re.fullmatch(r'\w{2,32}', emoji_new_name, re.ASCII):
            return await ctx.reply(f':x: `{emoji_new_name}` is not a valid emoji name to rename; use 2–32 English letters, numbers and underscores')

        guild = self.bot.get_guild(emoji['guild_id'])
        emoji = await guild.fetch_emoji(emoji['id'])

        if emoji:
            view = ViewConfirmation(ctx.author)
            reply = await ctx.reply(f'Do You really want to rename emoji\'s name to `{emoji_new_name}`?', view=view)
            await view.wait()

            if view.switch is None:
                await reply.edit(content=':x: Cancelled due to inactivity', view=None)
            elif view.switch is True:
                await reply.edit(content='Processing...', view=None)
                try:
                    new_emoji = await emoji.edit(name=emoji_new_name, reason=f'Renamed by {ctx.author.id}')
                except Exception as e:
                    await reply.edit(content=f':x: Emoji renaming was failed by Discord Error. Please contact to Bot Developer.\nError: {e}')
                else:
                    await self.db.rename_emoji(new_emoji.id, new_emoji.name)
                    await reply.edit(content=f':white_check_mark: Emoji {new_emoji} was renamed to `{new_emoji.name}`!')
            else:
                await reply.edit(content=':x: Cancelled.', view=None)
        else:
            await ctx.reply(f':x: {emoji_name} was not found in bot\'s servers. Please contact to Bot Developer.')

    @commands.command(name='delete', description='Deletes your emoji from bot')
    async def cmd_delete(self, ctx: commands.Context, name: str):
        emoji = await self.db.get_emoji(name)

        if emoji is None:
            return await ctx.reply(f':x: Emoji `{name}` not found in bot')

        if ctx.author.id not in cfg['bot']['supervisors']:
            if ctx.author.id != emoji['author_id']:
                return await ctx.reply(':x: That\'s not your emoji for deleting it')

        guild = self.bot.get_guild(emoji['guild_id'])
        emoji = await guild.fetch_emoji(emoji['id'])

        if emoji:
            view = ViewConfirmation(ctx.author)
            reply = await ctx.send(f'Do You really want to delete {emoji} emoji?', view=view)
            await view.wait()

            if view.switch is None:
                await reply.edit(content=':x: Cancelled due to inactivity', view=None)
            elif view.switch is True:
                await reply.edit(content='Deleting...', view=None)
                try:
                    await emoji.delete(reason=f'Deleted by {ctx.author.id}')
                except Exception as e:
                    await reply.edit(content=f':x: Emoji deletion was failed by Discord Error. Please contact to Bot Developer.\nError: {e}')
                else:
                    await self.db.delete_emoji(emoji.id)

                    if emoji.animated:
                        await self.db.decrease_usage_guild(emoji.guild_id, 'animated')
                    else:
                        await self.db.decrease_usage_guild(emoji.guild_id, 'static')

                    await reply.edit(content=f':white_check_mark: Emoji `{emoji.name}` was deleted from bot!')
            else:
                await reply.edit(content=':x: Cancelled', view=None)
        else:
            await ctx.reply(f':x: {name} was not found in bot\'s servers. Please contact to Bot Developer.')


def setup(bot: commands.Bot):
    cog = TextCmdsManage(bot)
    bot.add_cog(cog)
    log.info('Loaded')


def teardown(bot):
    log.info('Unloaded')
