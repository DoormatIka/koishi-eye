
import numpy as np
import imagehash

from PIL import Image, ImageFile, UnidentifiedImageError
from PIL.Image import Image as PILImage
from pathlib import Path

import logger
from hashers.types import CombinedImageHash, ImageHashResult

class ImageHasher:
    size: int
    log: logger.BlankLogger
    def __init__(self, log: logger.BlankLogger, size: int = 8):
        self.log = log
        self.size = size

    def create_hash_from_image(self, image_path: Path) -> ImageHashResult:
        ImageFile.LOAD_TRUNCATED_IMAGES = False

        try:
            with Image.open(image_path) as img:
                phash = self.global_phash(img)
                crophash = self.crop_resistant_hash(img)
                width, height = img.size

                return CombinedImageHash(
                    path=image_path,
                    hash=phash,
                    cropped_hash=crophash,
                    pixel_count=width * height
                ), None
        except (UnidentifiedImageError, OSError) as e:
            return None, str(e)

    def alpharemover(self, image: Image.Image):
        if image.mode == 'RGBA':
            return image.convert('RGB')
        return image

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



def imagehash_to_int(h: imagehash.ImageHash) -> int:
    arr = h.hash # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert isinstance(arr, np.ndarray)

    bits: np.typing.NDArray[np.bool_] = arr.astype(np.bool_, copy=False).ravel()

    packed: np.typing.NDArray[np.uint8] = np.packbits(bits)
    return int.from_bytes(packed.tobytes(), byteorder="big")



