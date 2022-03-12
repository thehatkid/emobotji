import logging
import aiomysql

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
