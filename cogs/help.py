import logging
import yaml
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)
cfg = yaml.safe_load(open('config.yml', 'r'))


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.PREFIX = cfg['bot']['prefix']
        self.INVITE_SERVER_URL = cfg['bot']['misc']['invite-server']
        self.INVITE_BOT_URL = cfg['bot']['misc']['invite-bot']

    @commands.group(invoke_without_command=True)
    async def help(self, ctx: commands.Context):
        embed = disnake.Embed(title=':information_source: Bot Help List', colour=disnake.Colour.blurple())
        embed.description = f'To see command usage: `{self.PREFIX}help <command>`'
        if self.INVITE_SERVER_URL:
            embed.description += f'\n\nNeed help? [Join to Support Server]({self.INVITE_SERVER_URL})'
        if self.INVITE_BOT_URL:
            embed.description += f'\n\nNeed invite bot? [Invite Bot]({self.INVITE_BOT_URL})'
        embed.add_field(
            name='Bot',
            value='`ping`, `stats`, `invite`, `support`, `react`',
            inline=False
        )
        embed.add_field(
            name='Emoji',
            value='`list`, `search`, `info`, `big`',
            inline=False
        )
        embed.add_field(
            name='Emoji Managment',
            value='`add`, `add-from-url`, `mark-nsfw`, `rename`, `delete`',
            inline=False
        )
        embed.set_footer(
            text='Requested by {0}#{1}'.format(
                ctx.author.name,
                ctx.author.discriminator
            ),
            icon_url=ctx.author.avatar
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='ping')
    async def help_ping(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Ping',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}ping`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Pings bot and shows an embed of Bot\'s Latency in milliseconds.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='react')
    async def help_react(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: React',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}react <name of emoji> <message id from this channel>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Reacts a Message (from current channel!) with emoji',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='stats')
    async def help_stats(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Statistics',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}stats`',
            inline=False
        )
        embed.add_field(
            name='Aliases',
            value='`stat`, `statistics`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Shows an Embed with Bot Statistics (Bot Uptime, Joined Servers, Emojis)',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='invite')
    async def help_invite(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Invite',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}invite`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Sends Bot Invite link in chat.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='support')
    async def help_support(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Support',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}support`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Sends Bot Owner\'s Discord Support Server in chat.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='list')
    async def help_list(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: List',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}list [<page of list>]`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Shows an Embed of Bot\'s list stored emojis.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='search')
    async def help_search(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Search Emoji',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}search <name/word of emoji>`',
            inline=False
        )
        embed.add_field(
            name='Aliases',
            value='`find`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Searchs Emoji with that name or by keyword in name.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='info')
    async def help_info(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Emoji Info',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}info <name of emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Shows an Embed of Emoji Info. Who are uploaded, when are uploaded and it\'s animated or not.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='big')
    async def help_big(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: "Big Image" of Emoji',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}big <name of emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Gets emoji\'s image and posts photo attachment.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='add')
    async def help_add(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Add',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}add <name of emoji> <custom emoji> [<is_nsfw? (yes/no)>]`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Adds custom emoji to bot for further using.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='add-from-url')
    async def help_addfromurl(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Add From URL',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}add-from-url <name of emoji> <url with image> [<is_nsfw? (yes/no)>]`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Adds custom emoji to bot from URL with Image.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='mark-nsfw')
    async def help_marknsfw(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Mark Emoji as NSFW',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}mark-nsfw <name of your emoji>`',
            inline=False
        )
        embed.add_field(
            name='Aliases',
            value='`nsfw`, `is-nsfw`, `toggle-nsfw`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Marks your uploaded emoji as NSFW, unmarks if already been NSFW marked.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='rename')
    async def help_rename(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Rename Emoji',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}rename <name of your emoji> <new name>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Renames your emoji to new name. Useful for fixing typo.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)

    @help.command(name='delete')
    async def help_delete(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Command: Delete Emoji',
            colour=disnake.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.PREFIX}delete <name of your emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Deletes your emoji forever from bot.',
            inline=False
        )
        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Help(bot))
    log.info('Loaded cog.')


def teardown(bot):
    log.info('Unloaded cog.')
