
import os
import random

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, Future, as_completed
from typing import Generic, TypeVar

from hashers.types import CombinedImageHash, ImageHashResult
from hashers.image import imagehash_to_int, ImageHasher

from finders.types import ImagePair
from finders.helpers import is_similar_image, get_supported_extensions

T = TypeVar('T')
class LSHBucket(Generic[T]):
    key_indexes: list[int]
    bucket: list[T] = []
    def __init__(self, key_indexes: list[int]):
        self.key_indexes = key_indexes
    def get_key_similarity(self, bin_val: list[bool]) -> int:
        """
            val should look like [True, False, True, False, False]
        """
        similarity = 0
        for index in self.key_indexes:
            if bin_val[index] == True:
                similarity += 1
        return similarity

def create_random_key_index() -> list[int]:
    resolution = 16
    return [random.randint(0, 63) for _ in range(resolution)]

type Bucket = LSHBucket[CombinedImageHash]
type Buckets = list[Bucket]

class LSHBucketFinder():
    hasher: ImageHasher
    buckets: Buckets
    def __init__(self, hasher: ImageHasher, resolution: int = 8):
        self.buckets = self._create_buckets_(resolution=resolution)
        self.hasher = hasher

    def _create_buckets_(self, resolution: int = 8):
        buckets: Buckets = list()
        lshbucket: Bucket = LSHBucket(key_indexes=create_random_key_index())

        for _ in range(0, resolution):
            buckets.append(lshbucket)
        return buckets

    # adding an image is an O(k) operation, where k is the number of buckets
    # compared to the brute force finder, where the same operation is O(1)
    def _add_image_to_buckets_(self, image_path: Path):
        res, err = self.hasher.create_hash_from_image(image_path)
        if res == None:
            self.hasher.log.warn(err or "Unknown error.")
            return

        matched: tuple[Bucket, int] | None = None
        # preprocessing step for buckets, unoptimized.
        bool_hash: list[bool] = res.hash.hash.flatten().tolist()
        for bucket in self.buckets: # getting the best match out of the buckets
            similarity = bucket.get_key_similarity(bool_hash)
            if matched != None and similarity > matched[1]:
                matched = (bucket, similarity)
            if matched == None:
                matched = (bucket, similarity)
                
        if matched != None: # pushing the image hash to the best matched bucket
            bucket, similarity = matched
            bucket.bucket.append(res)

    async def create_hashes_from_directory(self, directory: Path):
        exts = get_supported_extensions()

        n_thread = os.cpu_count()
        if n_thread == None:
            raise ValueError("OS cpu count cannot be found!")

        n_thread = max(n_thread - 2, 2)
        n_images = 0

        for ext in exts:
            for image_path in Path(directory).rglob(f"*{ext}"):
                pass
                

    def get_similar_objects(self, image_hashes: None):
        pass
