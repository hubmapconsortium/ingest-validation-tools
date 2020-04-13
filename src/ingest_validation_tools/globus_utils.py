import subprocess
from pathlib import Path


def get_globus_connection_error(origin):
    try:
        subprocess.run(
            ['globus', 'whoami'], check=True,
            stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return 'Run "globus login"'

    try:
        subprocess.run(
            ['globus', 'ls', origin], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.stdout

    return None


def get_globus_cache_path(origin, path):
    target = _get_cache_target(origin, path)
    if not target.exists():
        _cache_globus_origin_path(origin, path)
    return target


def _cache_globus_origin_path(origin, path):
    result = subprocess.run(
        ['globus', 'ls', '--recursive', f'{origin}:{path}'],
        check=True, text=True, capture_output=True)
    listing = result.stdout.split('\n')
    target = _get_cache_target(origin, path)
    for globus_path in listing:
        local_path = target / globus_path
        if globus_path.endswith('/'):
            local_path.mkdir(parents=True)
        else:
            local_path.touch()
            # Download *-metadata.tsv.


def _get_cache_target(origin, path):
    if path[0] == '/':
        path = path[1:]
    return Path(__file__).parent / 'globus-cache' / origin / path
