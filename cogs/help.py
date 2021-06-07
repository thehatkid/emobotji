import logging
import discord
from discord.ext import commands


log = logging.getLogger(__name__)


class Help(commands.Cog):
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
        embed.description = '**To see command usage:**\n`e!help <command>`'
        embed.add_field(
            name='Bot',
            value='`ping`',
            inline=False
        )
        embed.add_field(
            name='Emoji',
            value='`list`, `react`, `add`',
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
            value='`e!ping`',
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
            value='`e!list [<page of list>]`',
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
            value='`e!list <name of emoji> <message id from this channel>`',
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
            value='`e!list <name of emoji> <custom emoji>`',
            inline=False
        )
        embed.add_field(
            name='Description',
            value='Adds custom emoji to bot for further using.',
            inline=False
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
    log.info('Load cog.')


def teardown(bot):
    log.info('Unload cog.')
