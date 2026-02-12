

from pathlib import Path
from typing import Protocol, TypeVar, Generic
from src.hashers.types import CombinedImageHash

type ImagePair = tuple[CombinedImageHash, CombinedImageHash]

A = TypeVar('A')
Objects = TypeVar('Objects', covariant=True)
class FinderInterface(Protocol, Generic[A, Objects]):
    async def create_hashes_from_directory(self, directory: Path) -> A: ...
    def get_similar_objects(self, image_hashes: A) -> Objects: ...
