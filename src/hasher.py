
from dataclasses import dataclass
import numpy as np
import imagehash

from PIL import Image
from PIL.Image import Image as PILImage

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



class ImageHasher:
    size: int
    logger: logger.Logger
    def __init__(self, logger: logger.Logger, size: int = 8):
        self.logger = logger
        self.size = size

    def create_hashes_from_directory(self, directory: Path) -> list[CombinedImageHash]:
        exts = {"png", "jpg", "jpeg"}
        image_hashes: list[CombinedImageHash] = list()

        for ext in exts:
            image_paths = Path(directory).rglob(f"*.{ext}")
            for image_path in image_paths:
                img = Image.open(image_path)
                phash = self.global_phash(img)
                crophash = self.crop_resistant_hash(img)
                image_hashes.append(CombinedImageHash(path=image_path, hash=phash, cropped_hash=crophash))

                self.logger.print(f"[INFO] - hashing \"{image_path}\"")

        image_hashes.sort(key=lambda x: imagehash_to_int(x.hash))

        return image_hashes

    def get_similar_images(self, image_hashes: list[CombinedImageHash]) -> list[list[CombinedImageHash]]:
        nearest_matches: list[list[CombinedImageHash]] = list()
        MATCH_THRESHOLD = 5

        for i, img1 in enumerate(image_hashes):
            for img2 in image_hashes[i + 1:]:
                if img1.path == img2.path:
                    continue
                if abs(img1.hash - img2.hash) < MATCH_THRESHOLD:
                    nearest_matches.append([img1, img2])
                    matching_segments, distance = img1.cropped_hash.hash_diff(img2.cropped_hash)

                    self.logger.print(
                        f"[MATCH] - \n" +
                        f"\tLeft: {img1.path}\n" + 
                        f"\tRight: {img2.path}\n" + 
                        f"\tGlobal Difference: {abs(img1.hash - img2.hash)}\n" +
                        f"\tCropped Difference: (matching_segments: {matching_segments}, distance: {distance})\n"
                    )

        return nearest_matches

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
