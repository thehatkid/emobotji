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
        self.pool: aiomysql.Pool = None
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port

    async def connect(self) -> None:
        """Connects database for further using."""

        if self.pool is not None:
            raise exceptions.DatabaseAlreadyConnected

        try:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database
            )
        except aiomysql.MySQLError as e:
            logger.error(f'Failed to connect: {e}')
        else:
            logger.info('Successfully connected to database')

    async def disconnect(self) -> None:
        """Graceful disconnects database."""

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        await self.pool.close()
        await self.pool.wait_closed()

        self.pool = None

        logger.info('Disconnected from database')

    async def get_emoji(self, name: str) -> dict:
        """Retrieves full emoji entry by name from database.

        Parameters:
        -----------
        name: :class:`str`
            The emoji name to retrieve.

        Returns:
        --------
        :class:`dict`
            The dictionary with emoji entry.
        :class:`None`
            Emoji with given name was not found in database.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'SELECT * FROM `emojis` WHERE `name` = %s',
                    (name,)
                )
                row = await cursor.fetchone()

        if row is None:
            return None

        return {
            'id': row[0],
            'name': row[1],
            'animated': True if row[2] else False,
            'nsfw': True if row[3] else False,
            'formatted': '<{0}:{1}:{2}>'.format(
                'a' if row[2] else '', row[1], row[0]
            ),
            'created_at': row[4],
            'author_id': row[5],
            'guild_id': row[6]
        }

    async def get_formatted_emoji(self, name: str, nsfw: bool = False) -> str:
        """Retrieves formatted emoji for Discord messages.

        Parameters:
        -----------
        name: :class:`str`
            The emoji name to retrieve.
        nsfw: :class:`bool`
            Whether return NSFW emoji or not.

        Returns:
        --------
        :class:`str`
            The formatted emoji for Discord message.
        :class:`None`
            Emoji with given name was not found in database
            or is NSFW-only usage.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `name` = %s',
                    (name,)
                )
                row = await cursor.fetchone()

        if row is None:
            return None

        if nsfw is False and row[3] == 1:
            return None

        return '<{0}:{1}:{2}>'.format(
            'a' if row[2] else '', row[1], row[0]
        )

    async def get_emojis_counts(self) -> dict:
        """Retrieves total emoji count of static and animated usage
        in database.

        Returns:
        --------
        :class:`dict`
            The counts
            The dictionary with emoji usage counts.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
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
        """Retrieves available (not full) Guild ID for emoji addiction.

        Parameters:
        -----------
        which: :class:`bool`
            Whether `static` or `animated` for retrieving guild by type.

        Returns:
        --------
        :class:`int`
            The Guild ID of available guild.
        :class:`None`
            No available free guilds for addiction.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
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

        if row is None:
            return None

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

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
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
                await conn.commit()

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

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
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
                await conn.commit()

        return True

    async def get_emoji_list(self, nsfw: bool = False) -> list[tuple]:
        """Retrieves emoji list from database.

        Parameters:
        -----------
        nsfw: :class:`int`
            Whether also retrieve NSFW emojis or not.

        Returns:
        --------
        List[:class:`tuple`]
            The emoji entry from database.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if nsfw:
                    await cursor.execute(
                        'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` ORDER BY `name` ASC'
                    )
                else:
                    await cursor.execute(
                        'SELECT `id`, `name`, `animated`, `nsfw` FROM `emojis` WHERE `nsfw` = 0 ORDER BY `name` ASC'
                    )

                rows = await cursor.fetchall()

        return rows

    async def get_emoji_list_by_name(self, name: str, nsfw: bool = False) -> list[tuple]:
        """Retrieves emoji list by name from database.

        Parameters:
        -----------
        name: :class:`str`
            Name for search emojis by name.
        nsfw: :class:`int`
            Whether also retrieve NSFW emojis or not.

        Returns:
        --------
        List[:class:`tuple`]
            The emoji entry from database.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if nsfw:
                    await cursor.execute(
                        'SELECT `id`, `name`, `animated`, `nsfw`, `author_id` FROM `emojis` WHERE `name` LIKE %s ORDER BY `name` ASC',
                        (f'%{name}%',)
                    )
                else:
                    await cursor.execute(
                        'SELECT `id`, `name`, `animated`, `nsfw`, `author_id` FROM `emojis` WHERE `name` LIKE %s AND `nsfw` = 0 ORDER BY `name` ASC',
                        (f'%{name}%',)
                    )

                rows = await cursor.fetchall()

        return rows

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
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
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
                await conn.commit()

        return True

    async def rename_emoji(self, emoji_id: int, new_name: str) -> bool:
        """Renames emoji to new name.

        Parameters:
        -----------
        emoji_id: :class:`int`
            The emoji ID in database to rename.
        new_name: :class:`str`
            The new name of emoji.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'UPDATE `emojis` SET `name` = %s WHERE `id` = %s',
                    (new_name, emoji_id,)
                )

                # commit changes to database
                await conn.commit()

        return True

    async def delete_emoji(self, emoji_id: int) -> bool:
        """Deletes emoji from database irrevocably.

        Parameters:
        -----------
        emoji_id: :class:`int`
            The emoji ID in database to delete.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'DELETE FROM `emojis` WHERE `id` = %s',
                    (emoji_id,)
                )

                # commit changes to database
                await conn.commit()

        return True

    async def set_nsfw_mark(self, emoji_id: int, nsfw: bool) -> bool:
        """Marks or unmarks emoji as NSFW-only usage.

        Parameters:
        -----------
        emoji_id: :class:`int`
            The emoji ID in database to mark/unmark as NSFW-only.
        nsfw: :class:`bool`
            Whether the emoji is NSFW or not.
        """

        if self.pool is None:
            raise exceptions.DatabaseNotConnected

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'UPDATE `emojis` SET `nsfw` = %s WHERE `id` = %s',
                    (nsfw, emoji_id,)
                )

                # commit changes to database
                await conn.commit()

        return True
