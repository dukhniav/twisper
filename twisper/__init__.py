""" Twisper bot """
__version__ = '2022.12.dev'

if 'dev' in __version__:
    try:
        import subprocess

        __version__ = __version__ + '-' + subprocess.check_output(
            ['git', 'log', '--format="%h"', '-n 1'],
            stderr=subprocess.DEVNULL).decode("utf-8").rstrip().strip('"')

    except Exception:  # pragma: no cover
        # git not available, ignore
        pass