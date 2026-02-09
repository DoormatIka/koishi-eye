
from src.hashers.types import CombinedImageHash


class ModelImage(CombinedImageHash):
    def __init__(self, hash: CombinedImageHash):
        super().__init__(
            path=hash.path,
            hash=hash.hash,
            pixel_count=hash.pixel_count,
        )

