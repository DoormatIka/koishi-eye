
from queue import Queue
from typing import cast
import numpy as np
from numpy.typing import NDArray

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore

from hashers.types import CombinedImageHash, ImageHashResult
from hashers.image import ImageHasher

from finders.types import ImagePair
from finders.helpers import is_similar_image, get_supported_extensions

from .bucket import HammingBucket


type Bucket = HammingBucket[CombinedImageHash]
type Buckets = list[Bucket]

# this entire class relies on an assumption that LSH can have their similarity detected
# with a random portion of their hash being matched.
class HammingClustererFinder():
    hasher: ImageHasher
    buckets: Buckets
    def __init__(self, hasher: ImageHasher, resolution: int = 8):
        self.buckets = self._create_buckets_(resolution=resolution)
        self.hasher = hasher

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

    async def create_hashes_from_directory(self, directory: Path) -> Buckets:
        exts = get_supported_extensions()
        # Limit the queue so threads don't hash 10,000 images before you can save 10
        result_queue: Queue[tuple[Path, ImageHashResult | None]] = Queue(maxsize=50)

        def producer(path: Path):
            """Runs in a thread: Hashes the image and puts result in queue."""
            try:
                res = self.hasher.create_hash_from_image(path)

                # blocks if the queue is full.
                result_queue.put((path, res))
            except Exception as e:
                self.hasher.log.warn(f"Hash failed for {path}: {e}")
                result_queue.put((path, None))

        with ThreadPoolExecutor(max_workers=4) as executor:
            for ext in exts:
                for image_path in Path(directory).rglob(f"*{ext}"):
                    _ = executor.submit(producer, image_path)
            
            # A tiny hack: tell the consumer loop when the pool is finished
            # We do this by submitting a task that waits for the pool to drain 
            # or simply letting the main thread handle the loop logic.
            
            tasks_submitted = sum(1 for ext in exts for _ in Path(directory).rglob(f"*{ext}"))
            
            for _ in range(tasks_submitted):
                _, res = result_queue.get() # Waits for the next result
                if res == None:
                    continue
                c, _ = res
                if c == None:
                    continue
                
                self._add_image_to_buckets_(combined=c)
                result_queue.task_done()

        return self.buckets

    def get_similar_objects(self, image_hashes: Buckets) -> set[ImagePair]:
        nearest_matches: set[ImagePair] = set()

        for container in image_hashes:
            # assuming the images are arranged to their closest container.
            for i, img1 in enumerate(container.bucket):
                for img2 in container.bucket[i + 1:]:
                    pair = tuple(sorted([str(img1.path), str(img2.path)]))
                    if pair in nearest_matches:
                        continue

                    if is_similar_image(img1, img2) != None:
                        nearest_matches.add((img1, img2))

        return nearest_matches
                

def nparr_bool_to_int(arr: np.ndarray):
    packed = np.packbits(arr)
    return int.from_bytes(packed.tobytes(), byteorder="big")



