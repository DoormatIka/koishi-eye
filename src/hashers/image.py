
import numpy as np
import imagehash

from PIL import Image, ImageFile, UnidentifiedImageError
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
            phash = self.global_phash(image_path)

            return CombinedImageHash(
                path=image_path,
                hash=phash,
                pixel_count=100 # PLACEHOLDER
            ), None
        except (UnidentifiedImageError, OSError) as e:
            return None, str(e)

    def alpharemover(self, image: Image.Image):
        if image.mode != 'RGBA':
            return image
        canvas = Image.new('RGBA', image.size, (255, 255, 255, 255))
        canvas.paste(image, mask=image)
        return canvas.convert('RGB')

    def _pil_grayscale_convert_to_np_arr(self, p: Path):
        with Image.open(p) as img:
            grayscale_img = img.convert('L')

            resized_img = grayscale_img.resize((self.size, self.size), Image.Resampling.NEAREST)
            del grayscale_img

            arr = np.array(resized_img, dtype=np.uint8)
            del resized_img

            return arr

    def global_phash(self, p: Path) -> imagehash.ImageHash:
        """
        Converts an image into a perceptual hash.
        """
        arr = self._pil_grayscale_convert_to_np_arr(p)

        img = Image.new(mode="L", size=(self.size, self.size))
        quantiles = np.arange(100)
        quantiles_values = np.percentile(arr, quantiles)
        zdata = (np.interp(arr, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
        img.putdata(zdata.flatten())

        hashed = imagehash.phash(image=img)
        del img

        return hashed

def imagehash_to_int(h: imagehash.ImageHash) -> int:
    arr = h.hash # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    assert isinstance(arr, np.ndarray)

    bits: np.typing.NDArray[np.bool_] = arr.astype(np.bool_, copy=False).ravel()

    packed: np.typing.NDArray[np.uint8] = np.packbits(bits)
    return int.from_bytes(packed.tobytes(), byteorder="big")



