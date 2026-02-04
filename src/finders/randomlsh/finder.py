
import random

from pathlib import Path

from hashers.types import CombinedImageHash
from hashers.image import ImageHasher

from finders.types import ImagePair
from finders.helpers import is_similar_image, get_supported_extensions

from .bucket import LSHBucket


# this is a very rudimentary LSH.

type Bucket = LSHBucket[CombinedImageHash]
type Buckets = list[Bucket]

# this entire class relies on an assumption that LSH can have their similarity detected
# with a random portion of their hash being matched.
class RandomLSHFinder():
    hasher: ImageHasher
    buckets: Buckets
    def __init__(self, hasher: ImageHasher, resolution: int = 8):
        self.buckets = self._create_buckets_(resolution=resolution)
        self.hasher = hasher

    def _create_buckets_(self, resolution: int = 8):
        buckets: Buckets = list()
        chunk_size = 64

        for i in range(resolution):
            start = i * chunk_size
            end = start + chunk_size
            indices = list(range(start, end))

            lshbucket: Bucket = LSHBucket(key_indexes=indices)
            buckets.append(lshbucket)
        return buckets

    def _get_closest_matched_bucket_(self, bool_hash: list[bool]) -> Bucket | None:
        if not self.buckets:
            return None
                
        return max(self.buckets, key=lambda b: b.get_key_similarity(bool_hash))

    # adding an image is an O(k) operation, where k is the number of buckets
    # compared to the brute force finder, where the same operation is O(1)
    def _add_image_to_buckets_(self, image_path: Path):
        res, err = self.hasher.create_hash_from_image(image_path)
        if res == None:
            self.hasher.log.warn(err or "Unknown error.")
            return

        bool_hash: list[bool] = res.hash.hash.flatten().tolist()
        container = self._get_closest_matched_bucket_(bool_hash=bool_hash)
        if container != None: # pushing the image hash to the best matched bucket
            container.bucket.append(res)

    async def create_hashes_from_directory(self, directory: Path) -> Buckets:
        exts = get_supported_extensions()

        for ext in exts:
            for image_path in Path(directory).rglob(f"*{ext}"):
                self._add_image_to_buckets_(image_path=image_path)

        return self.buckets

    def get_similar_objects(self, image_hashes: Buckets) -> list[ImagePair]:
        nearest_matches: list[ImagePair] = list()

        for container in image_hashes:
            # assuming the images are arranged to their closest container.
            for i, img1 in enumerate(container.bucket):
                for img2 in container.bucket[i + 1:]:
                    if is_similar_image(img1, img2) != None:
                        nearest_matches.append((img1, img2))

        return nearest_matches
                

def create_random_key_index() -> list[int]:
    resolution = 16
    return [random.randint(0, 63) for _ in range(resolution)]


