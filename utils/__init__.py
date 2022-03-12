def human_readable_size(bytes_count: int, decimal_places: int = 2) -> str:
    for unit in ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if bytes_count < 1024.0 or unit == 'PiB':
            break
        bytes_count /= 1024.0
    return f'{bytes_count:.{decimal_places}f} {unit}'
