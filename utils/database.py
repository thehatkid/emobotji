import logging
import aiomysql
from datetime import datetime

from . import exceptions

logger = logging.getLogger('database')


class Database:
    """Representation of MySQL database wrapper for Emobotji."""

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 3306,
        user: str = None,
        password: str = None,
        database: str = None
    ) -> None:
        self.conn: aiomysql.Connection = None
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port

    async def connect(self) -> None:
        """Connects database for further using."""

        if self.conn is not None:
            raise exceptions.DatabaseAlreadyConnected

        try:
            self.conn = await aiomysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.database
            )
        except aiomysql.MySQLError as e:
            logger.error(f'Failed to connect: {e}')
        else:
            logger.info('Successfully connected to database')

    async def disconnect(self) -> None:
        """Disconnects database."""

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        await self.conn.ensure_closed()
        self.conn = None

        logger.info('Disconnected from database')

    async def get_emoji(self, name: str) -> dict:
        """Fetch full emoji entry by name from database.

        Returns :class:`dict` if was found otherwise :class:`None`.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                'SELECT * FROM `emojis` WHERE `name` = %s',
                (name,)
            )
            row = await cursor.fetchone()

        if row is not None:
            return {
                'id': row[0],
                'name': row[1],
                'animated': True if row[2] else False,
                'nsfw': True if row[3] else False,
                'created_at': row[4],
                'author_id': row[5],
                'guild_id': row[6]
            }
        else:
            return None

    async def get_formatted_emoji(self, name: str, nsfw: bool = False) -> str:
        """Fetch formatted emoji only by name from database.
        Useful for apply in Discord message.

        Returns :class:`str` if was found otherwise :class:`None`.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` = %s',
                (name,)
            )
            row = await cursor.fetchone()

        if row is not None:
            if nsfw is False and row[3] == 1:
                return None
            else:
                return '<{0}:{1}:{2}>'.format(
                    'a' if row[2] else '',
                    row[1],
                    row[0]
                )
        else:
            return None

    async def get_emojis_counts(self) -> dict:
        """Fetch emoji total count in database.

        Returns :class:`dict` with emoji total count.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            await cursor.execute("""
            SELECT (
                SELECT COUNT(*) FROM `emojis`
            ) AS emojis_total, (
                SELECT COUNT(*) FROM `emojis` WHERE `nsfw` = 0
            ) AS emojis_total_sfw, (
                SELECT COUNT(*) FROM `emojis` WHERE `nsfw` = 1
            ) AS emojis_total_nsfw
            """)
            row = await cursor.fetchone()

            return {
                'total': row[0],
                'total_sfw': row[1],
                'total_nsfw': row[2]
            }

    async def get_available_guild(self, which: str) -> int:
        """Returns available, not full Guild ID for emoji uploading.

        Parameters:
        -----------
        which: :class:`str`
            Type of emoji to get guild: `static`, `animated`.

        Returns:
        --------
        :class:`int` of available, not full Guild ID for emoji uploading.

        :class:`None` if there's no available free guilds for uploading.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            if which == 'static':
                await cursor.execute(
                    'SELECT `guild_id` FROM `guilds` WHERE `usage_static` < 50 ORDER BY `number` ASC LIMIT 1'
                )
            elif which == 'animated':
                await cursor.execute(
                    'SELECT `guild_id` FROM `guilds` WHERE `usage_animated` < 50 ORDER BY `number` ASC LIMIT 1'
                )
            else:
                raise exceptions.UnknownType(which)

            row = await cursor.fetchone()

        return row[0]

    async def increase_usage_guild(self, guild_id: int, which: str) -> bool:
        """Increases static or animated emoji usage for guild.
        
        Parameters:
        -----------
        guild_id: :class:`int`
            Guild ID to increase emoji usage.
        which: :class:`str`
            Type of emoji to increase: `static`, `animated`.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            if which == 'static':
                await cursor.execute(
                    'UPDATE `guilds` SET `usage_static` = `usage_static` + 1 WHERE `guild_id` = %s',
                    (guild_id,)
                )
            elif which == 'animated':
                await cursor.execute(
                    'UPDATE `guilds` SET `usage_animated` = `usage_animated` + 1 WHERE `guild_id` = %s',
                    (guild_id,)
                )
            else:
                raise exceptions.UnknownType(which)

        # commit changes to database
        await self.conn.commit()

        return True

    async def decrease_usage_guild(self, guild_id: int, which: str) -> bool:
        """Decreases static or animated emoji usage for guild.
        
        Parameters:
        -----------
        guild_id: :class:`int`
            Guild ID to decrease emoji usage.
        which: :class:`str`
            Type of emoji to decrease: `static`, `animated`.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            if which == 'static':
                await cursor.execute(
                    'UPDATE `guilds` SET `usage_static` = `usage_static` - 1 WHERE `guild_id` = %s',
                    (guild_id,)
                )
            elif which == 'animated':
                await cursor.execute(
                    'UPDATE `guilds` SET `usage_animated` = `usage_animated` - 1 WHERE `guild_id` = %s',
                    (guild_id,)
                )
            else:
                raise exceptions.UnknownType(which)

        # commit changes to database
        await self.conn.commit()

        return True

    async def add_emoji(
        self,
        emoji_id: int,
        emoji_name: str,
        animated: bool,
        nsfw: bool,
        created_at: datetime,
        author_id: int,
        guild_id: int
    ) -> bool:
        """Adds emoji to database for further usage.

        Parameters:
        -----------
        emoji_id: :class:`int`
            Discord Emoji ID.
        emoji_name: :class:`str`
            Discord Emoji Name for usage and finding.
        animated: :class:`bool`
            Whether the emoji is animated or not.
        nsfw: :class:`bool`
            Whether the emoji is NSFW or not.
        created_at: :class:`datetime`
            The emoji creation time object.
        author_id: :class:`int`
            Discord Author ID for emoji owner.
        guild_id: :class:`int`
            The Guild ID determines in which guild was created emoji.

        Returns:
        --------
        :class:`bool` `True` if successful otherwise raise exception.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            query = 'INSERT INTO `emojis` (`id`, `name`, `animated`, `nsfw`, `created`, `author_id`, `guild_id`) VALUES (%s, %s, %r, %r, %s, %s, %s)'
            params = (
                emoji_id,
                emoji_name,
                animated,
                nsfw,
                created_at,
                author_id,
                guild_id,
            )
            await cursor.execute(query, params)

        # commit changes to database
        await self.conn.commit()

        return True

    async def rename_emoji(self, emoji_id: int, new_name: str) -> bool:
        """Renames emoji to new name.

        Parameters:
        -----------
        emoji_id: :class:`int`
            The emoji ID in database to rename.
        new_name: :class:`str`
            The new name of emoji.

        Returns:
        --------
        :class:`bool` `True` if successful otherwise raise exception.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                'UPDATE `emojis` SET `name` = %s WHERE `id` = %s',
                (new_name, emoji_id,)
            )

        # commit changes to database
        await self.conn.commit()

        return True

    async def delete_emoji(self, emoji_id: int) -> bool:
        """Deletes emoji from database irrevocably.

        Parameters:
        -----------
        emoji_id: :class:`int`
            The emoji ID in database to delete.

        Returns:
        --------
        :class:`bool` `True` if successful otherwise raise exception.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                'DELETE FROM `emojis` WHERE `id` = %s',
                (emoji_id,)
            )

        # commit changes to database
        await self.conn.commit()

        return True

    async def set_nsfw_mark(self, emoji_id: int, nsfw: bool) -> bool:
        """Marks or unmarks emoji as NSFW-only usage.

        Parameters:
        -----------
        emoji_id: :class:`int`
            The emoji ID in database to mark/unmark as NSFW-only.
        nsfw: :class:`bool`
            Whether the emoji is NSFW or not.

        Returns:
        --------
        :class:`bool` `True` if successful otherwise raise exception.
        """

        if self.conn is None:
            raise exceptions.DatabaseNotConnected

        async with self.conn.cursor() as cursor:
            await cursor.execute(
                'UPDATE `emojis` SET `nsfw` = %s WHERE `id` = %s',
                (nsfw, emoji_id,)
            )

        # commit changes to database
        await self.conn.commit()

        return True
