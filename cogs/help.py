import logging
from os import environ
import discord
from discord.ext import commands


log = logging.getLogger(__name__)


class Help(commands.Cog):
    def __init__(self, _):
        self.prefix = environ.get('BOT_PREFIX')

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        embed = discord.Embed(
            title=':information_source: Bot\'s Help List',
            colour=discord.Colour.blurple()
        )
        embed.description = f'**To see command usage:**\n`{self.prefix}help <command>`'
        embed.add_field(
            name='Bot',
            value='`ping`, `react`',
            inline=False
        )
        embed.add_field(
            name='Emoji',
            value='`list`, `search`, `info`, `big`',
            inline=False
        )
        embed.add_field(
            name='Emoji Managment',
            value='`add`, `add-from-url`',
            inline=False
        )
        embed.set_footer(
            text='Requested by {0}#{1}'.format(ctx.author.name, ctx.author.discriminator),
            icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @help.command(name='ping')
    async def help_ping(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: Ping',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}ping`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Pings bot, shows bot\'s latency in milliseconds.',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='react')
    async def help_react(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: React',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}list <name of emoji> <message id from this channel>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Reacts message (from current channel!) with emoji',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='list')
    async def help_list(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: List',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}list [<page of list>]`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Shows list of bot\'s stored emojis.',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='search')
    async def help_search(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: Search Emoji',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}search <name of emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Searchs emoji with that name or by keyword in name.',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='info')
    async def help_info(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: Emoji Info',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}info <name of emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Gets emoji info. Who are uploaded, when are uploaded and it\'s animated or not.',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='big')
    async def help_big(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: "Big Image" of Emoji',
            colour=discord.Colour.blurple()
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
        await ctx.send(embed=embed)

    @help.command(name='add')
    async def help_add(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: Add',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}add <name of emoji> <custom emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Adds custom emoji to bot for further using.',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='add-from-url')
    async def help_addfromurl(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: Add From URL',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}add-from-url <name of emoji> <url with image>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Adds custom emoji to bot from URL with Image.',
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
