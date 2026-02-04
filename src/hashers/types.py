
from pathlib import Path
from dataclasses import dataclass
from typing import override

import imagehash

@dataclass
class CombinedImageHash:
    path: Path
    hash: imagehash.ImageHash
    pixel_count: int
    @override
    def __hash__(self) -> int:
        return hash(self.path)
    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CombinedImageHash):
            return NotImplemented
        return self.path == other.path

type ImageHashResult = tuple[CombinedImageHash, None] | tuple[None, str]
