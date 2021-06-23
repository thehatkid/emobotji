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
        embed.set_footer(
            text='Requested by {0}#{1}'.format(
                ctx.author.name, ctx.author.discriminator
            ),
            icon_url=ctx.author.avatar_url
        )
        embed.description = f'**To see command usage:**\n`{self.prefix}help <command>`'
        embed.add_field(
            name='Bot',
            value='`ping`',
            inline=False
        )
        embed.add_field(
            name='Emoji',
            value='`list`, `search`, `react`, `add`, `add-from-url`',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command()
    async def ping(self, ctx):
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

    @help.command()
    async def list(self, ctx):
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

    @help.command()
    async def react(self, ctx):
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

    @help.command()
    async def add(self, ctx):
        embed = discord.Embed(
            title=':information_source: Command: Add',
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name='Usage',
            value=f'`{self.prefix}list <name of emoji> <custom emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Adds custom emoji to bot for further using.',
            inline=False
        )
        await ctx.send(embed=embed)

    @help.command(name='add-from-url')
    async def add_from_url(self, ctx):
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

    @help.command()
    async def search(self, ctx):
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

def setup(bot):
    bot.add_cog(Help(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
