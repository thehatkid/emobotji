import logging
import yaml
from os import environ
import disnake
from disnake.ext import commands


log = logging.getLogger(__name__)

cfg = yaml.safe_load(open('config.yml', 'r'))


class Help(commands.Cog):
    def __init__(self, _):
        self.prefix = cfg['bot']['prefix']

    @commands.group(invoke_without_command=True)
    async def help(self, ctx: commands.Context):
        embed = disnake.Embed(
            title=':information_source: Bot Help List',
            colour=disnake.Colour.blurple()
        )
        # You can edit here, replace your links or remove it.
        embed.description = (
            f'*To see command usage:*\n`{self.prefix}help <command>`\n\n'
            '[Support Server](https://discord.gg/Y7EtGn6bH3) | [Invite Bot](https://top.gg/bot/841879090038177792)'
        )
        embed.add_field(
            name='Bot',
            value='`ping`, `stats`, `react`',
            inline=False
        )
        embed.add_field(
            name='Emoji',
            value='`list`, `search`, `info`, `big`',
            inline=False
        )
        embed.add_field(
            name='Emoji Managment',
            value='`add`, `add-from-url`, `mark-nsfw`',
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
            value=f'`{self.prefix}ping`',
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
            value=f'`{self.prefix}react <name of emoji> <message id from this channel>`',
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
            value=f'`{self.prefix}stats`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Shows an Embed with Bot Statistics (Bot Uptime, Joined Servers, Emojis)',
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
            value=f'`{self.prefix}list [<page of list>]`',
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
            value=f'`{self.prefix}search <name/word of emoji>`',
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
            value=f'`{self.prefix}info <name of emoji>`',
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
            value=f'`{self.prefix}big <name of emoji>`',
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
            value=f'`{self.prefix}add <name of emoji> <custom emoji> [<is_nsfw? (yes/no)>]`',
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
            value=f'`{self.prefix}add-from-url <name of emoji> <url with image> [<is_nsfw? (yes/no)>]`',
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
            value=f'`{self.prefix}mark-nsfw <name of your emoji>`',
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


def setup(bot):
    bot.add_cog(Help(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
