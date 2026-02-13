
import asyncio
import numpy as np
import os

from collections.abc import Generator, Iterable
from typing import TypeVar, cast
from numpy.typing import NDArray

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from itertools import islice

from src.gui.infra.logger import Error, HasherLogger, Info, Progress
from src.hashers import ImageHashResult
from src.hashers.types import CombinedImageHash
from src.hashers.image import ImageHasher

from src.finders.types import ImagePair
from src.finders.helpers import is_similar_image, get_supported_extensions

from .bucket import HammingBucket


type Bucket = HammingBucket[CombinedImageHash]
type Buckets = list[Bucket]

# this entire class relies on an assumption that LSH can have their similarity detected
# with a random portion of their hash being matched.
class HammingClustererFinder():
    hasher: ImageHasher
    buckets: Buckets
    logger: HasherLogger
    def __init__(self, hasher: ImageHasher, logger: HasherLogger, resolution: int = 8):
        self.buckets = self._create_buckets_(resolution=resolution)
        self.hasher = hasher
        self.logger = logger

    def _create_buckets_(self, resolution: int):
        buckets: Buckets = list()
        chunk_size = 64 // resolution

        for i in range(resolution):
            start = i * chunk_size
            end = start + chunk_size if i < resolution - 1 else 63
            indices = list(range(start, end))

            lshbucket: Bucket = HammingBucket(key_indexes=indices)
            buckets.append(lshbucket)
        return buckets

    def _get_closest_matched_bucket_(self, bool_hash: int) -> Bucket | None:
        if not self.buckets:
            return None
                
        return max(self.buckets, key=lambda b: b.get_key_similarity(bool_hash))

    # adding an image is an O(k) operation, where k is the number of buckets
    # compared to the brute force finder, where the same operation is O(1)
    def _add_image_to_buckets_(self, combined: CombinedImageHash, top_k: int = 2):
        hash = cast(NDArray[np.bool], combined.hash.hash)
        
        key: int = nparr_bool_to_int(hash)

        scored_buckets = [
            (b.get_key_similarity(key), b)
            for b in self.buckets
        ]
        scored_buckets.sort(key=lambda x: x[0], reverse=True)

        for i in range(min(top_k, len(scored_buckets))):
            _, container = scored_buckets[i]
            container.bucket.append(combined)

    def clear_buckets(self):
        for bucket in self.buckets:
            bucket.bucket.clear()

    async def create_hashes_from_directory(self, directory: Path) -> Buckets:
        self.clear_buckets()
        await self.logger.notify(Info(msg="Getting files from disk"))

        exts = get_supported_extensions()

        path_generator = (p for ext in exts for p in Path(directory).rglob(f"*{ext}"))

        """
        cpu_count = os.cpu_count() or 1
        if cpu_count > 1:
            await self._create_hashes_multithreading(path_generator)
        else:
            await self._create_hashes_singlethreaded(path_generator)
        """

        await self._create_hashes_singlethreaded(path_generator)

        return self.buckets

    async def _create_hashes_singlethreaded(self, path_generator: Generator[Path, None, None]):
        n_images = 0
        for path_chunk in chunked(path_generator, size=8):
            for res, err in _process_chunk(self.hasher, path_chunk):
                if res is None:
                    await self.logger.notify(Error(str(err)))
                    continue

                self._add_image_to_buckets_(combined=res)
                n_images += 1

                if n_images % 10 == 0:
                    await self.logger.notify(Progress(
                        path=res.path,
                        is_complete=False,
                        current=n_images
                    ))

                await asyncio.sleep(0) # event loop breathing room

        await self.logger.notify(Progress(
            path=Path(),
            is_complete=True,
            current=n_images
        ))

    async def _create_hashes_multithreading(self, path_generator: Generator[Path, None, None]):
        n_images = 0
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as executor:
            futures: list[asyncio.Future[list[ImageHashResult]]] = []
            for path_chunk in chunked(path_generator, size=8):
                future = loop.run_in_executor(executor, _process_chunk, self.hasher, path_chunk)
                futures.append(future)

            for completed_future in asyncio.as_completed(futures):
                chunk_results = await completed_future
                for res, err in chunk_results:
                    if res is None:
                        await self.logger.notify(Error(str(err)))
                        continue
                    
                    self._add_image_to_buckets_(combined=res)
                    n_images += 1

                    if n_images % 10 == 0:
                        _ = asyncio.create_task(
                            self.logger.notify(Progress(
                                path=res.path,
                                is_complete=False,
                                current=n_images
                            ))
                        )


        _ = asyncio.create_task(
            self.logger.notify(Progress(
                path=Path(),
                is_complete=True,
                current=n_images
            ))
        )

    def get_similar_objects(self, image_hashes: Buckets) -> set[ImagePair]:
        nearest_matches: set[ImagePair] = set()
        path_matches: set[tuple[str, ...]] = set()


        for container in image_hashes:
            # assuming the images are arranged to their closest container.
            for i, img1 in enumerate(container.bucket):
                for img2 in container.bucket[i + 1:]:
                    pair = tuple(sorted([str(img1.path), str(img2.path)]))
                    if pair in path_matches:
                        continue

                    if is_similar_image(img1, img2) is not None:
                        nearest_matches.add((img1, img2))
                        path_matches.add(pair)

        return nearest_matches

def _process_chunk(hasher: ImageHasher, paths: list[Path]):
    # This runs in the worker process
    return [hasher.create_hash_from_image(p) for p in paths]

def nparr_bool_to_int(arr: np.ndarray):
    packed = np.packbits(arr)
    return int.from_bytes(packed.tobytes(), byteorder="big")

T = TypeVar("T")
def chunked(iterable: Iterable[T], size: int):
    it = iter(iterable)
    while item := list(islice(it, size)):
        yield item
