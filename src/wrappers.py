
from pathlib import Path

from src.gui.infra.logger import Logger
from collections.abc import Collection

from finders import HammingClustererFinder, Buckets, BruteForceFinder, FinderInterface, ImagePair
from hashers import ImageHasher, CombinedImageHash

from typing import override
from enum import Enum



class MethodAction(Enum):
    BRUTE = "brute"
    HAMMING = "hamming"
    @override
    def __str__(self) -> str:
        return self.value


async def brute_force(directory: Path):
    log = Logger()
    imghasher = ImageHasher(size=16)
    bf: FinderInterface[list[CombinedImageHash], list[ImagePair]] = BruteForceFinder(hasher=imghasher, logger=log)

    hashes = await bf.create_hashes_from_directory(directory)
    similar_images = bf.get_similar_objects(hashes)

    return similar_images

async def clusterer(directory: Path):
    log = Logger()
    imghasher = ImageHasher(size=16)
    bf: FinderInterface[Buckets, set[ImagePair]] = HammingClustererFinder(hasher=imghasher, logger=log)

    hashes = await bf.create_hashes_from_directory(directory)
    similar_images = bf.get_similar_objects(hashes)

    return similar_images

async def scan_from_directory(directory: Path, choice: MethodAction) -> Collection[ImagePair]: # prototype
    print(f"[START] - Parsing through {directory}")
    if choice == MethodAction.BRUTE:
        return await brute_force(directory)
    if choice == MethodAction.HAMMING:
        return await clusterer(directory)
