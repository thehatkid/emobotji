import asyncio
import aiohttp

def human_readable_size(bytes_count: int, decimal_places: int = 2) -> str:
    for unit in ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if bytes_count < 1024.0 or unit == 'PiB':
            break
        bytes_count /= 1024.0
    return f'{bytes_count:.{decimal_places}f} {unit}'


async def fetch_image(session: aiohttp.ClientSession, url: str) -> tuple:
    async with session.get(url) as response:
        if response.status == 200:
            if response.headers['content-type'] not in ['image/png', 'image/jpeg', 'image/gif']:
                return (False, 1)

            animated = True if response.headers['content-type'] == 'image/gif' else False
            image = await response.read()

            return (True, animated, image)
        return (False, 2, response.status)
