
from dataclasses import dataclass
import os
from typing import Protocol
import numpy as np
import imagehash

from PIL import Image, UnidentifiedImageError
from PIL.Image import Image as PILImage
from concurrent.futures import ProcessPoolExecutor, Future, as_completed
from pathlib import Path


import logger

@dataclass
class CombinedImageHash:
    path: Path
    cropped_hash: imagehash.ImageMultiHash
    hash: imagehash.ImageHash

def imagehash_to_int(h: imagehash.ImageHash) -> int:
    arr = h.hash # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert isinstance(arr, np.ndarray)

    bits: np.typing.NDArray[np.bool_] = arr.astype(np.bool_, copy=False).ravel()

    packed: np.typing.NDArray[np.uint8] = np.packbits(bits)
    return int.from_bytes(packed.tobytes(), byteorder="big")


# todo: crop resistant hashing doesn't do anything at the moment.
# have a flag that says what hash triggered the nearest match.


class FinderInterface(Protocol):
    def create_hashes_from_directory(self, directory: Path) -> list[CombinedImageHash]: ...
    def get_similar_images(self, image_hashes: list[CombinedImageHash]) -> list[list[CombinedImageHash]]: ...

class BruteForceFinder:
    hasher: ImageHasher
    def __init__(self, hasher: ImageHasher):
        self.hasher = hasher

    def create_hashes_from_directory(self, directory: Path) -> list[CombinedImageHash]:
        exts = {"png", "jpg", "jpeg"}
        image_hashes: list[CombinedImageHash] = list()

        n_thread = os.cpu_count()
        if n_thread == None:
            raise ValueError("OS cpu count cannot be found!")

        n_thread = max(n_thread, 2)
        n_thread = 1
        with ProcessPoolExecutor(max_workers=n_thread) as executor:
            futures: list[Future[ImageHashResult]] = list()
            for ext in exts:
                for image_path in Path(directory).rglob(f"*.{ext}"):
                    futures.append(executor.submit(self.hasher.create_hash_from_image, image_path))

            for future in as_completed(futures):
                result, err = future.result()
                if result != None:
                    self.hasher.logger.info(f"hashing \"{result.path}\"")
                    image_hashes.append(result)
                else:
                    self.hasher.logger.warn(err or "")

        image_hashes.sort(key=lambda x: imagehash_to_int(x.hash))

        return image_hashes


    def get_similar_images(self, image_hashes: list[CombinedImageHash]) -> list[ImagePair]:
        nearest_matches: list[ImagePair] = list()

        with ProcessPoolExecutor(max_workers=1) as executor:
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
                self.hasher.logger.match(
                    f"\tLeft: {img1.path}\n" + 
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
        

class ANNFinder:
    pass

type ImagePair = tuple[CombinedImageHash, CombinedImageHash]
type ImageHashResult = tuple[CombinedImageHash, None] | tuple[None, str]

class ImageHasher:
    size: int
    logger: logger.Logger
    def __init__(self, logger: logger.Logger, size: int = 8):
        self.logger = logger
        self.size = size

    def create_hash_from_image(self, image_path: Path) -> ImageHashResult:
        try:
            img = Image.open(image_path)
            phash = self.global_phash(img)
            crophash = self.crop_resistant_hash(img)

            return CombinedImageHash(path=image_path, hash=phash, cropped_hash=crophash), None
        except (UnidentifiedImageError, OSError) as e:
            return None, str(e)

    def alpharemover(self, image: Image.Image):
        if image.mode != 'RGBA':
            return image
        canvas = Image.new('RGBA', image.size, (255, 255, 255, 255))
        canvas.paste(image, mask=image)
        return canvas.convert('RGB')

    def global_phash(self, img: PILImage):
        img = img.convert('L').resize((self.size, self.size), Image.Resampling.NEAREST)

        data = np.ascontiguousarray(img.get_flattened_data()).reshape(-1)
        quantiles = np.arange(100)
        quantiles_values = np.percentile(data, quantiles)
        zdata = (np.interp(data, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
        img.putdata(zdata)

        return imagehash.phash(image=img)

    def crop_resistant_hash(self, img: PILImage) -> imagehash.ImageMultiHash:
        image = self.alpharemover(img)
        return imagehash.crop_resistant_hash(image=image, min_segment_size=100) # pyright: ignore[reportUnknownMemberType]


