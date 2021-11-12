import disnake


VIEW_EMOJIS = {
    # You can put your emoji into this dictonary for using somewhere... :/
    'next': disnake.PartialEmoji(
        name="page_next",
        animated=False,
        id=870595469536006154
    ),
    'prev': disnake.PartialEmoji(
        name="page_prev",
        animated=False,
        id=870595458010058782
    ),
    'close': disnake.PartialEmoji(
        name="page_close",
        animated=False,
        id=870595479505887303
    )
}


class ViewPaginator(disnake.ui.View):
    """Disnake View Paginator."""

    def __init__(self, author: disnake.User, embeds: list[disnake.Embed], entries: int, page: int = 0, timeout: int = 120):
        """
        Parameters
        ----------
        author: :class:`~disnake.User`
            Discord User object.
        embeds: :class:`list[disnake.Embed]`
            Embeds for pagination.
        entries: :class:`int`
            Entries count for preview.
        page: :class:`int`
            Starting embed page.
        timeout: :class:`int`
            Timeout seconds.
        """
        super().__init__(timeout=timeout)
        self.author = author
        self.embeds = embeds
        self.entries = entries
        self.page = page

        # Set footer to first embed
        self.embeds[page].set_footer(text=f'Page {self.page + 1} of {len(self.embeds)} ({self.entries} entries)')

        # If have only one embed, disable all navigation buttons
        if len(self.embeds) <= 1:
            self.children[0].disabled = True
            self.children[1].disabled = True
        # If first page, disable "Previous" button
        elif self.page == 0:
            self.children[0].disabled = True
            self.children[1].disabled = False
        # If last page, disable "Next" button
        elif self.page == len(self.embeds) - 1:
            self.children[0].disabled = False
            self.children[1].disabled = True

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        # If Sender's User ID is not equals with User ID from Interaction...
        if self.author.id != interaction.author.id:
            # Interaction checks fails
            await interaction.response.send_message(
                content=':x: You can\'t press buttons belong command sender.',
                ephemeral=True
            )
            return False
        # Interaction checks passes
        return True

    async def on_timeout(self):
        embed = disnake.Embed(
            title=':x: List was closed.',
            description='Reason: `Automatically closed due to inactivity.`',
            colour=disnake.Colour.dark_red()
        )
        await self.msg.edit(embed=embed, view=None)

    @disnake.ui.button(emoji=VIEW_EMOJIS['prev'], style=disnake.ButtonStyle.gray)
    async def page_prev(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.page == 0:
            await interaction.response.defer()
        else:
            self.page -= 1
            # If first page, disable "Previous" button
            if self.page == 0:
                self.children[0].disabled = True
                self.children[1].disabled = False
            # Else enable all navigation buttons
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = self.embeds[self.page]
            embed.set_footer(text=f'Page {self.page + 1} of {len(self.embeds)} ({self.entries} entries)')
            await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji=VIEW_EMOJIS['next'], style=disnake.ButtonStyle.gray)
    async def page_next(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.page == len(self.embeds) - 1:
            await interaction.response.defer()
        else:
            self.page += 1
            # If last page, disable "Next" button
            if self.page == len(self.embeds) - 1:
                self.children[0].disabled = False
                self.children[1].disabled = True
            # Else enable all navigation buttons
            else:
                self.children[0].disabled = False
                self.children[1].disabled = False
            embed = self.embeds[self.page]
            embed.set_footer(text=f'Page {self.page + 1} of {len(self.embeds)} ({self.entries} entries)')
            await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji=VIEW_EMOJIS['close'], style=disnake.ButtonStyle.red)
    async def page_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title=':x: List was closed.',
            description='Reason: `Closed by User.`',
            colour=disnake.Colour.dark_red()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
