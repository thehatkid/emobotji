def human_readable_size(bytes: int, decimal_places: int = 2) -> str:
    for unit in ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if bytes < 1024.0 or unit == 'PiB':
            break
        bytes /= 1024.0
    return f'{bytes:.{decimal_places}f} {unit}'
