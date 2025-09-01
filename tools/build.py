import argparse
import compileall
import os
import pathlib
import shutil

parser = argparse.ArgumentParser(description="Build a Sims 4 mod")
parser.add_argument("--root", required=True, help="Root folder of the mod")
parser.add_argument("--name", required=True, help="Name of the mod")


PYTHON_MAGIC = ".cpython-37"

def build():
    args = parser.parse_args()

    # compileall python files in root folder
    compileall.compile_dir(args.root, force=True)

    # create mod directory
    mod_dir = f"build/{args.name}"
    os.makedirs(mod_dir, exist_ok=True)

    # copy all compiled files to mod directory with the directory structure but removing __pycache__
    for file in pathlib.Path(args.root).rglob("*.pyc"):
        dest = pathlib.Path(mod_dir) / file.relative_to(file.anchor)
        dest = dest.with_name(dest.name.replace("__pycache__", ""))
        dest = dest.with_name(dest.name.replace(PYTHON_MAGIC, ""))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file, dest)

if __name__ == "__main__":
    build()
