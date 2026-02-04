
from typing import Generic, TypeVar

T = TypeVar('T')
class HammingBucket(Generic[T]):
    key_indexes: list[int]
    signature: int
    mask: int
    bucket: list[T]
    def __init__(self, key_indexes: list[int]):
        self.key_indexes = key_indexes
        self.mask = 0
        for i in self.key_indexes:
            self.mask |= (1 << i)
        self.signature = self.mask
        self.bucket = []
    def get_key_similarity(self, bin_val: int) -> int:
        differences = (bin_val ^ self.signature) & self.mask
        
        return len(self.key_indexes) - differences.bit_count()
