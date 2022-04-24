import disnake
from disnake.ext import commands
from typing import Mapping
from typing import Optional
from typing import List


class HelpCommand(commands.HelpCommand):
    """Emobotji Help Command for discord.py framework."""

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]):
        ctx = self.context
        help_command = f'{ctx.clean_prefix}{ctx.command.name}'

        help_content = f'**Hello, {ctx.author.mention}! Welcome to the bot help page.**\n\n'
        help_content += ':warning: **Please use the Application (Slash) Commands.**\n\n'
        help_content += f'Use `{help_command} <command>` for get more info on a command.\n\n'
        help_content += '**Usage legend:**\n'
        help_content += '- `<argument>` - This means the argument is __required__.\n'
        help_content += '- `[argument]` - This means the argument is __optional__.\n\n'
        help_content += '**Bot Commands:**'

        embed = disnake.Embed(
            title=':information_source: Bot Help',
            colour=disnake.Colour.dark_blue(),
            description=help_content
        )
        embed.set_footer(
            text=f'Bot help requested by {ctx.author}',
            icon_url=ctx.author.display_avatar
        )

        for cog, cmds in mapping.items():
            if isinstance(cog, commands.Cog):
                if len(cmds) > 0:
                    cmds_inline = ', '.join([f'`{cmd.name}`' for cmd in cmds])
                    embed.add_field(
                        name=f'{cog.qualified_name} ({len(cmds)})',
                        value=cmds_inline,
                        inline=False
                    )

        await ctx.reply(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        ctx = self.context
        help_command = f'{ctx.clean_prefix}{ctx.command.name}'

        embed = disnake.Embed(
            title=f':information_source: Commands of Cog: `{cog.qualified_name}`',
            color=disnake.Color.dark_blue(),
            description=f'Use `{help_command} <command>` for get more info on a command.'
        )
        embed.set_footer(
            text=f'Cog help requested by {ctx.author}',
            icon_url=ctx.author.display_avatar
        )
        embed.add_field(
            name='Commands',
            value=', '.join([f'`{cmd.name}`' for cmd in cog.walk_commands()]),
            inline=False
        )

        await ctx.reply(embed=embed)

    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        signature = self.get_command_signature(command)

        embed = disnake.Embed(
            title=f':information_source: Command Help: `{command.name}`',
            color=disnake.Color.dark_blue(),
            description=command.description
        )
        embed.set_footer(
            text=f'Command help requested by {ctx.author}',
            icon_url=ctx.author.display_avatar
        )

        if command.aliases:
            embed.description += f'\n\n*(this command have {len(command.aliases)} command aliases, see in brackets)*'

        embed.add_field(
            name='Usage',
            value=f'`{signature}`',
            inline=False
        )

        await ctx.reply(embed=embed)

    async def send_error_message(self, error: str):
        await self.context.reply(f':x: {error}')
