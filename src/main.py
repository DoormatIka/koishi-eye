from collections.abc import Collection
from typing import cast
import argparse
import flet as ft

from pathlib import Path
from typing import override
from enum import Enum

import logger

from gui import flet_config, flet_main
from finders import HammingClustererFinder, Buckets, BruteForceFinder, FinderInterface, ImagePair
from hashers import ImageHasher, CombinedImageHash

import asyncio

class MethodAction(Enum):
    BRUTE = "brute"
    HAMMING = "hamming"
    @override
    def __str__(self) -> str:
        return self.value

parser = argparse.ArgumentParser(description="Fuzzy duplicate image finder.")
_ = parser.add_argument("-i", "--input", 
                        help="A folder to scan.")
_ = parser.add_argument("-d", "--delete", 
                        action='store_true', 
                        help="Enable automatic deletion of files.")
_ = parser.add_argument("-m", "--method", 
                        type=MethodAction, 
                        choices=list(MethodAction), 
                        help="Choose what method to scan the folder with.")

async def brute_force(directory: Path):
    imghasher = ImageHasher(log=logger.MatchLogger(), size=16)
    bf: FinderInterface[list[CombinedImageHash], list[ImagePair]] = BruteForceFinder(hasher=imghasher)

    hashes = await bf.create_hashes_from_directory(directory)
    similar_images = bf.get_similar_objects(hashes)

    return similar_images

async def clusterer(directory: Path):
    imghasher = ImageHasher(log=logger.MatchLogger(), size=16)
    bf: FinderInterface[Buckets, set[ImagePair]] = HammingClustererFinder(hasher=imghasher)

    hashes = await bf.create_hashes_from_directory(directory)
    similar_images = bf.get_similar_objects(hashes)

    return similar_images

async def scan_from_directory(directory: Path, choice: MethodAction) -> Collection[ImagePair]: # prototype
    print(f"[START] - Parsing through {directory}")
    if choice == MethodAction.BRUTE:
        return await brute_force(directory)
    if choice == MethodAction.HAMMING:
        return await clusterer(directory)

async def main():
    args = parser.parse_args()
    _is_delete = bool(args.delete) # pyright: ignore[reportAny]
    inp = str(args.input) # pyright: ignore[reportAny]
    method = cast(MethodAction, args.method)
    if len(inp) <= 0:
        parser.print_help()
        return
    dir_path = Path(inp)
    if not dir_path.is_dir():
        parser.print_help()
        return

    nearest_matches = await scan_from_directory(dir_path, choice=method)
    for img1, img2 in nearest_matches:
        print(
            f"Left: {img1.path}\n" + 
                f"\tRight: {img2.path}\n" + 
                f"\tGlobal Difference: {abs(img1.hash - img2.hash)}\n"
        )
    print(f"{len(nearest_matches)} matches found. Finished.")

def quality_test_fn():
    imghasher = ImageHasher(log=logger.Logger(), size=16)

    h1, err = imghasher.create_hash_from_image(Path("/home/mualice/Downloads/G_Cfm4LbgAA9BrY.png"))
    h2, err = imghasher.create_hash_from_image(Path("/home/mualice/Downloads/G_Cfm4LbgAA9BrY (copy).jpg"))
    if h1 != None and h2 != None:
        print(h2.hash - h1.hash)
    else:
        print(err)

if __name__ == "__main__":
    _ = ft.run(before_main=flet_config, main=flet_main) # gui builder
    # _ = ft.run(gui.gui.flet_main) # gui builder
    # quality_test_fn()
    asyncio.run(main())

