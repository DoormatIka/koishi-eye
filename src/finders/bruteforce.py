
import os

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, Future, as_completed

from PIL import Image

from hashers.types import CombinedImageHash, ImageHashResult
from hashers.image import imagehash_to_int, ImageHasher

from finders.types import ImagePair

# todo: crop resistant hashing doesn't do anything at the moment.
# have a flag that says what hash triggered the nearest match.


class BruteForceFinder:
    hasher: ImageHasher
    def __init__(self, hasher: ImageHasher):
        self.hasher = hasher

    async def create_hashes_from_directory(self, directory: Path) -> list[CombinedImageHash]:
        exts = get_supported_extensions()
        image_hashes: list[CombinedImageHash] = list()

        n_thread = os.cpu_count()
        if n_thread == None:
            raise ValueError("OS cpu count cannot be found!")

        n_thread = max(n_thread - 2, 2)
        with ProcessPoolExecutor(max_workers=n_thread) as executor:
            futures: list[Future[ImageHashResult]] = list()
            for ext in exts:
                for image_path in Path(directory).rglob(f"*{ext}"):
                    futures.append(executor.submit(self.hasher.create_hash_from_image, image_path))

            for future in as_completed(futures):
                result, err = future.result()
                if result != None:
                    self.hasher.log.info(f"hashing \"{result.path}\"")
                    image_hashes.append(result)
                else:
                    self.hasher.log.warn(err or "")

        image_hashes.sort(key=lambda x: imagehash_to_int(x.hash))

        return image_hashes


    def get_similar_objects(self, image_hashes: list[CombinedImageHash]) -> list[ImagePair]:
        nearest_matches: list[ImagePair] = list()

        with ProcessPoolExecutor() as executor:
            futures: list[Future[ImagePair | None]] = list()
            for i, img1 in enumerate(image_hashes):
                for img2 in image_hashes[i + 1:]:
                    futures.append(executor.submit(is_similar_image, img1, img2))

            for future in as_completed(futures):
                val = future.result()
                if val == None:
                    continue
                img1, img2 = val
                matching_segments, distance = img1.cropped_hash.hash_diff(img2.cropped_hash)
                self.hasher.log.match(
                    f" Left: {img1.path}\n" + 
                    f"\tRight: {img2.path}\n" + 
                    f"\tGlobal Difference: {abs(img1.hash - img2.hash)}\n" +
                    f"\tCropped Difference: (matching_segments: {matching_segments}, distance: {distance})\n"
                )
                nearest_matches.append((img1, img2))

        return nearest_matches



def is_similar_image(img1: CombinedImageHash, img2: CombinedImageHash) -> ImagePair | None:
    MATCH_THRESHOLD = 5
    if img1.path != img2.path and abs(img1.hash - img2.hash) < MATCH_THRESHOLD:
        return img1, img2
    return None

def get_supported_extensions():
    ext_reading = {ext for ext, fmt in Image.registered_extensions().items() if fmt in Image.OPEN}
    return ext_reading       

