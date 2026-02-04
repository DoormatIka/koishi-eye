

from imagehash import ImageHash
from hashers.image import ImageHasher


class LSHIndex:
    hasher: ImageHasher
    band_width: int
    overlap: int
    def __init__(self, hasher: ImageHasher, band_width: int = 16, overlap: int = 8):
        self.hasher = hasher
        self.band_width = band_width
        self.overlap = overlap
        self.storage = {}
    def _get_overlapping_bands(self, hash_obj: ImageHash):
        hash_obj.hash
        pass
