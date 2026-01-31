import logger
import argparse
from pathlib import Path

from finders.types import ImagePair
import hashers.image
import finders.bruteforce
import gui.gui
import gui.config

import flet as ft

parser = argparse.ArgumentParser(description="Fuzzy duplicate image finder.")
_ = parser.add_argument("-i", "--input", help="A folder to scan.")
_ = parser.add_argument("-d", "--delete", action='store_true', help="Enable automatic deletion of files.")

async def scan_from_directory(directory: Path, _is_delete: bool = False) -> list[ImagePair]: # prototype
    print(f"[START] - Parsing through {directory}")

    imghasher = hashers.image.ImageHasher(log=logger.MatchLogger(), size=16)
    bf = finders.bruteforce.BruteForceFinder(hasher=imghasher)

    hashes = await bf.create_hashes_from_directory(directory)
    similar_images = bf.get_similar_objects(hashes)

    return similar_images

def main():
    args = parser.parse_args()
    is_delete = bool(args.delete) # pyright: ignore[reportAny]
    inp = str(args.input) # pyright: ignore[reportAny]
    if inp:
        dir_path = Path(inp)
        if dir_path.is_dir():
            _ = scan_from_directory(dir_path, _is_delete=is_delete)
            print("Finished.")
        else:
            parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    _ = ft.run(before_main=gui.config.config, main=gui.gui.flet_main) # gui builder
    # main()

