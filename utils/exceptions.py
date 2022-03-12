class DatabaseAlreadyConnected(Exception):
    """Raised when the database is already connected."""

    def __init__(self):
        pass

    def __str__(self):
        return 'Database is already connected'


class DatabaseNotConnected(Exception):
    """Raised when the database is not connected."""

    def __init__(self):
        pass

    def __str__(self):
        return 'Database is not connected'
