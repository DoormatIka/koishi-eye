
import os

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, Future, as_completed

from cli.logger import Error, Info, Progress
from hashers.types import CombinedImageHash, ImageHashResult
from hashers.image import imagehash_to_int, ImageHasher

from finders.types import ImagePair
from finders.helpers import is_similar_image, get_supported_extensions


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

        await self.hasher.log.notify(Info(msg="Started hashes from directory."))


        n_thread = max(n_thread - 2, 2)
        n_images = 0
        with ProcessPoolExecutor(max_workers=n_thread) as executor:
            futures: list[Future[ImageHashResult]] = list()
            for ext in exts:
                for image_path in Path(directory).rglob(f"*{ext}"):
                    futures.append(executor.submit(self.hasher.create_hash_from_image, image_path))

            for future in as_completed(futures):
                result, err = future.result()
                if result != None:
                    n_images += 1
                    await self.hasher.log.notify(Progress(
                        path=result.path,
                        current=n_images,
                        is_complete=True,
                    ))
                    image_hashes.append(result)
                else:
                    await self.hasher.log.notify(Error(err or ""))

        image_hashes.sort(key=lambda x: imagehash_to_int(x.hash))

        await self.hasher.log.notify(Progress(
            path=Path(),
            current=n_images,
            is_complete=False,
        ))

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
                nearest_matches.append((img1, img2))

        return nearest_matches




