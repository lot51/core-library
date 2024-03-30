import os


def get_mod_root(file, depth=2):
    """
    Get the path to the directory a ts4script is located. By default, assumes the file
    is located at a depth of 2 (in the root of a package inside a compiled ts4script).

    Increase the depth if you are fetching the mod root from another level deep
    inside your mod, or running the mod decompiled.

    For example:
        - Scripts/lot51_core/__init__.py is at a depth of 2
        - Scripts/lot51_core/lib/zone.py is at a depth of 3

    Usage: get_mod_root(__file__)

    :param file: The path to the current file, usually __file__
    :param depth: The depth `file` is located relative to Mods folder.
    :return: str
    """
    root = os.path.abspath(os.path.realpath(file))
    if '.ts4script' in root.lower():
        depth += 1

    for depth in range(depth):
        root = os.path.dirname(root)

    return root


def get_game_dir():
    """
    Get the path to the Game documents directory that includes Mods, localthumbcache, and other files.
    :return: str
    """
    root = get_mod_root(__file__, depth=3)
    search = os.path.join('The Sims 4', 'Mods')
    attempt = 0
    while not root.endswith(search) and attempt < 10:
        attempt += 1
        root = os.path.dirname(root)
    return os.path.dirname(root)
