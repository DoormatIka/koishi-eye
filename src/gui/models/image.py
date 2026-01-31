
from hashers.types import CombinedImageHash


class ModelImage(CombinedImageHash):
    is_delete: bool = False
    def __init__(self, hash: CombinedImageHash):
        super().__init__(
            path=hash.path,
            cropped_hash=hash.cropped_hash,
            hash=hash.hash,
            pixel_count=hash.pixel_count,
        )

    def toggle_delete(self) -> bool:
        self.is_delete = not self.is_delete
        return self.is_delete

