import os


def get_mod_root(file, depth=2):
    root = os.path.realpath(file)
    if '.ts4script' in root.lower():
        depth += 1

    for depth in range(depth):
        root = os.path.dirname(root)

    return root